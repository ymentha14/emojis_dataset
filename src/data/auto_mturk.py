"""
Script to automate the creation of MTURK task: this assumes you did run the app script
generating the forms and their associate file previously.
"""
import os.path
import pickle as pk
import time
from datetime import datetime

import boto3
import pandas as pd
import pytz
import xmltodict
from time import sleep

from src.constants import (AWS_KEYS_PATH, CREDS_PATH, URL_INDEX_PATH,HIT2FORM_PATH,FORMS_RESULTS_DIR,HONEYPOTS)
from src.data.auto_drive import get_drive_service, download_drive_txt, download_drive_spreadsheet,download_all_csv_results
from src.data.fraudulous import detect_repeat_frauders,detect_honey_frauders

from src.utils import generate_password, read_access_keys
from pathlib import Path
from IPython.display import clear_output

utc=pytz.UTC

def create_mturk_client(aws_access_key_id,aws_secret_access_key,production=False):
    """
    Return an MTURK client

    Args:
        aws_access_key_id (str): aws key
        aws_secret_access_key (str): secret aws key
        production (Bool): sandbox if set to false

    Returns:
        client (boto3.client)
    """
    create_hits_in_production = False
    environments = {
            "production": {
                "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
                "preview": "https://www.mturk.com/mturk/preview"
            },
            "sandbox": {
                "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
                "preview": "https://workersandbox.mturk.com/mturk/preview"
            },
    }
    mturk_environment = environments["production"] if create_hits_in_production else environments["sandbox"]

    client = boto3.client(
       'mturk',
       aws_access_key_id = aws_access_key_id,
       aws_secret_access_key = aws_secret_access_key,
       region_name='us-east-1',
       endpoint_url = mturk_environment['endpoint'],
    )
    return client

def monitor_worker_tags(client,qualification_type_id='3OR1BBO28PIVPWZMRDTWE8U6OZXNGN'):
    """
    Function to run in a separate thread: tag every worker who completed one of the hit with
    a qualification preventing him to complete another emoji-related hit

    Args:
        qualification_type_id (str): id of the qualification_type
    """
    print("searching..")
    while True:
        time.sleep(1)
        # search for workers already tagged
        exworkers = set()
        qualifs = client.list_workers_with_qualification_type(QualificationTypeId=qualification_type_id,)
        for qualif in qualifs['Qualifications']:
            if qualif['QualificationTypeId'] == qualification_type_id:
                exworkers.add(qualif['WorkerId'])

        # search for new workers
        worker_ids = set()
        for hit in client.list_hits()['HITs']:
            hitid = hit['HITId']
            result = client.list_assignments_for_hit(HITId=hitid,AssignmentStatuses=['Submitted','Approved','Rejected'])
            assignments = result['Assignments']

            for assignment in assignments:
                workerid = assignment['WorkerId']
                worker_ids.add(workerid)

        worker_ids = worker_ids - exworkers
        for workerid in worker_ids:
            print(f"Tagging worker {workerid}")
            client.associate_qualification_with_worker(
            QualificationTypeId=qualification_type_id,
            WorkerId=workerid,
            IntegerValue=1,
            SendNotification=False
        )

def get_answer(answer):
        xml_doc = xmltodict.parse(answer)
        return xml_doc['QuestionFormAnswers']['Answer']['FreeText']

class Watcher():
    """
    Class to monitor the workers who complete more than a defined threshold
    of our tasks ==> tag them to prevent them from keeping answering
    """
    def __init__(self,form_results_path,
                    url_results,
                    drive_service,
                    threshold=2,
                    production=False):
        self.production = production
        # retrieval of the access keys
        aws_access_key_id,aws_secret_access_key = read_access_keys(AWS_KEYS_PATH)
        # creation of an self.client client
        self.client = create_mturk_client(aws_access_key_id,aws_secret_access_key,production)
        self.threshold = threshold
        self.form_results_path = form_results_path
        self.url_results = url_results
        self.drive_service = drive_service

    def get_workers2tag(self):
        download_all_csv_results(self.url_results,
                                self.form_results_path,
                                self.drive_service)
        meta_df = []
        for form_path in self.form_results_path.iterdir():
            df = pd.read_csv(form_path,usecols=['Worker ID'])
            meta_df.append(df)
        meta_df = pd.concat(meta_df,axis=0)
        # number of different
        forms_count = meta_df['Worker ID'].value_counts()
        forms_count = forms_count[forms_count > self.threshold]
        return set(forms_count.index.tolist())

    def get_tagged_workers(self,qualification_type_id='3OR1BBO28PIVPWZMRDTWE8U6OZXNGN'):
        # search for workers already tagged
        exworkers = set()
        qualifs = self.client.list_workers_with_qualification_type(QualificationTypeId=qualification_type_id,)
        for qualif in qualifs['Qualifications']:
            if qualif['QualificationTypeId'] == qualification_type_id:
                exworkers.add(qualif['WorkerId'])
        return exworkers

    def monitor(self,qualification_type_id='3OR1BBO28PIVPWZMRDTWE8U6OZXNGN'):
        # search for workers already tagged
        i = 0
        while True:
            print(f"{i} th iteration")
            # information comes from google drive
            tagged_workers = self.get_tagged_workers()
            workers2tag = self.get_workers2tag()
            # remove the workers already tagged
            workers2tag = workers2tag - tagged_workers
            for workerid in workers2tag:
                print(f"Tagging worker {workerid}")
                # TODO: do a try except to catch a wrongly typed workerid
                self.client.associate_qualification_with_worker(
                    QualificationTypeId=qualification_type_id,
                    WorkerId=workerid,
                    IntegerValue=1,
                    SendNotification=False
                )
            clear_output(wait=True)
            i+=1
            sleep(5)

class Turker():
    def __init__(self,hitlayout,
                    MaxAssignments,
                    LifetimeInSeconds,
                    AutoApprovalDelayInSeconds,
                    AssignmentDurationInSeconds,
                    Reward,
                    production=False):
        """
        Args:
            hittypeid (str): hittypeid of the template to use
            hitlayout (str): hitlayout of the template to use
            lifetimeinsec (int): lifetime in seconds
        """
        self.production = production
        # retrieval of the access keys
        aws_access_key_id,aws_secret_access_key = read_access_keys(AWS_KEYS_PATH)
        # creation of an self.client client
        self.MaxAssignments = MaxAssignments
        self.client = create_mturk_client(aws_access_key_id,aws_secret_access_key,production)
        self.hitlayout = hitlayout
        self.LifetimeInSeconds = LifetimeInSeconds
        self.AutoApprovalDelayInSeconds = AutoApprovalDelayInSeconds
        self.AssignmentDurationInSeconds = AssignmentDurationInSeconds
        self.Reward = Reward
        self.url = "https://workersandbox.mturk.com/mturk/preview?groupId="# if production else "https://worker.mturk.com/mturk/preview?groupId="
        if HIT2FORM_PATH.exists():
            print("Loading hit2form")
            self.hit2form = pk.load(open(HIT2FORM_PATH,"rb"))
        else:
            self.hit2form = {}

    def get_url(self,hit_id):
        hit = self.client.get_hit(HITId=hit_id)
        return self.url + hit['HIT']['HITGroupId']

    def list_hits(self):
        hits = self.client.list_hits()['HITs']
        if len(hits) == 0:
            print("No Hits available")
        else:

            expiration = hits[0]['Expiration'].replace(tzinfo=utc)
            now =  datetime.now().replace(tzinfo=utc)
            if expiration < now:
                print("EXPIRED")
            else:
                delay = expiration - now
                delay = int(delay.total_seconds()) / 60
                print(f"Expiration:{expiration.strftime('%b %d %Y %H:%M:%S')} ({delay:.2f} minutes left)")
            df = []
            for hit in hits:
                row = {}
                hitid = hit['HITId']
                row['FormIdx'] = self.hit2form[hitid]
                row['HITId'] = hitid
                row['Status'] = hit['HITStatus']
                comp = self.client.list_assignments_for_hit(HITId=hitid, AssignmentStatuses=['Submitted','Approved','Rejected'])['NumResults']
                row['Completed'] = comp
                maxo = hit["MaxAssignments"]
                row['Percent_completed'] = int(comp / maxo*100)
                df.append(row)
            df = (pd.DataFrame(df)
                .set_index('FormIdx')
                .sort_index()
                )
            return df


    def list_results(self,hit_id):
        worker_results = self.client.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted','Approved','Rejected'])
        if worker_results['NumResults'] > 0:
            df = []
            for assignment in worker_results['Assignments']:
                answer = get_answer(assignment['Answer'])
                password = generate_password(self.hit2form[hit_id])
                df.append({'WorkerId':assignment['WorkerId'],
                           'HITId':hit_id,
                           'Answer':answer,
                           'Code':password,
                           'Status':assignment['AssignmentStatus']
                          })
            return pd.DataFrame(df)
        else:
            print(f"No results ready yet for {hit_id}")

    def list_all_results(self):
        df = []
        hits = self.client.list_hits()['HITs']
        if len(hits) == 0:
            print("No results")
            return None
        for hit in hits:
            hit_id = hit['HITId']
            df.append(self.list_results(hit_id))
        df = pd.concat(df,axis=0)
        return df

    def __approve_all_assignments(self,hit_id):

        """

        Args:
            correct_hits (Bool): whether to correct correct hits exclusively
        """
        assignments = self.client.list_assignments_for_hit(HITId=hit_id,AssignmentStatuses=['Submitted'])
        assignments = assignments['Assignments']
        for assignment in assignments:
            ass_id = assignment['AssignmentId']
            print(f"Approving assignment {ass_id}")
            self.client.approve_assignment(AssignmentId=ass_id)

    def approve_correct_assignments(self,hit_id):

        """
        Args:
            correct_hits (Bool): whether to correct correct hits exclusively
        """
        form_idx = self.hit2form[hit_id]
        form_path = FORMS_RESULTS_DIR.joinpath(f"{form_idx}.csv")
        form_df = pd.read_csv(form_path)

        assignments = self.client.list_assignments_for_hit(HITId=hit_id,AssignmentStatuses=['Submitted'])
        assignments = assignments['Assignments']

        # workers = set([assignment['WorkerID'] for assignment in assignments])

        password_frauders = self.detect_password_frauders(assignments=assignments,
                                                            password = generate_password(form_idx))
        honey_frauders = detect_honey_frauders(form_df,HONEYPOTS)
        repeat_frauders = detect_repeat_frauders(form_df)
        frauders = password_frauders.union(honey_frauders).union(repeat_frauders)

        for assignment in assignments:
            ass_id = assignment['AssignmentId']
            worker_id = assignment['WorkerID']
            if worker_id in frauders:
                RequesterFeedback = ""
                if worker_id in password_frauders:
                    RequesterFeedback += "Invalid confirmation key.\n"

                if worker_id in honey_frauders:
                    RequesterFeedback += "Non valid obvious emoji answer.\n"

                if worker_id in repeat_frauders:
                    RequesterFeedback += "Too many times the same word.\n"
                self.client.reject_assignment(AssignmentId=ass_id,
                                                RequesterFeedback=RequesterFeedback)
            else:
                print(f"Approving assignment {ass_id}")
                self.client.approve_assignment(AssignmentId=ass_id)

    def detect_password_frauders(self,assignments,password):
        password_frauders = set()
        for assignment in assignments:
            worker_id = assignment['WorkerID']
            answer = get_answer(assignment['Answer'])
            if answer != password:
                password_frauders.update(worker_id)
        return password_frauders

    def approve_all_hits(self):
        hits = self.client.list_reviewable_hits()['HITs']
        for hit in hits:
            self.__approve_all_assignments(hit['HITId'])

    def approve_correct_hits(self):
        hits = self.client.list_reviewable_hits()['HITs']
        for hit in hits:
            self.approve_correct_assignments(hit['HITId'])

    def delete_all_hits(self):
        hits = self.client.list_hits()['HITs']
        for hit in hits:
            self.delete_hit(hit['HITId'])

    def delete_hit(self,hit_id):
        try:
            self.client.delete_hit(HITId=hit_id)
            del self.hit2form[hit_id]
            self.__update_hit2form()

            print(f"Deleting hit {hit_id}")
        except:
            print(f"Hit {hit_id} in Unassignable mode")

    def __update_hit2form(self):
        pk.dump(self.hit2form,open(HIT2FORM_PATH,"wb"))

    def stop_all_hits(self):
        hits = self.client.list_hits()['HITs']
        for hit in hits:
            self.stop_hit(hit['HITId'])

    def stop_hit(self,hit_id):
        status= self.client.get_hit(HITId=hit_id)['HIT']['HITStatus']
        # If HIT is active then set it to expire immediately
        if status=='Assignable' or status=='Unassignable':
            self.client.update_expiration_for_hit(
                HITId=hit_id,
                ExpireAt=datetime(2015, 1, 1)
            )
            print(f"Stop hit {hit_id}")

    def approve_delete_all_hits(self):
        self.approve_all_hits()
        self.delete_all_hits()

    def create_forms_hits(self,forms_url,hittypeid=None,hitlayout=None):
        """
        Args:
            forms_url(dict): mapping between forms index and their respective url
        """
        hitlayout = self.hitlayout if hitlayout is None else hitlayout
        for idx,url in forms_url.items():
            print(f"Creating hit for form {idx}")

            myhit = self.client.create_hit(
                        MaxAssignments=self.MaxAssignments,
                        LifetimeInSeconds = self.LifetimeInSeconds,
                        AutoApprovalDelayInSeconds=self.AutoApprovalDelayInSeconds,
                        AssignmentDurationInSeconds=self.AssignmentDurationInSeconds,
                        Reward=self.Reward,
                        HITLayoutId=hitlayout,
                        HITLayoutParameters = [{'Name':'url',
                                   'Value':url}],
                        Title=f'Emojis Descriptions n {idx}',
                        Keywords='emojis, description, sentiment, emotions',
                        Description='Describe emojis by a single accurate word',
                        QualificationRequirements=[
                            {
                                'QualificationTypeId': '3OR1BBO28PIVPWZMRDTWE8U6OZXNGN',
                                'Comparator': 'DoesNotExist',
                                'ActionsGuarded': 'DiscoverPreviewAndAccept'
                            }
                        # TODO: add location and hit percentage
                        ]
            )
            self.hit2form[myhit['HIT']['HITId']] = idx
        self.__update_hit2form()

def clean_own_worker(client,QualificationTypeId='3OR1BBO28PIVPWZMRDTWE8U6OZXNGN'):
    """
    Remove the epfl.dlab worker qualification for debugging purpose
    """
    try:
        client.disassociate_qualification_from_worker(
            WorkerId='A29C1XYH77RQYM',
            QualificationTypeId=QualificationTypeId,
            Reason=''
        )
    except:
        print("Worker already clean")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--id',
        help="gdrive id of the urls file",
        default='11UjUJ9WfafdMEXZww9Q9GBnXsqX0dPWPdZGXGfFr_t4',
        type=str
    )
    parser.add_argument(
        '--hittype',
        help="HITTypeId of the MTurk HIT",
        type=str,
        required=True
    )
    parser.add_argument(
        '--hitlayout',
        help="HITLayoutID of the MTurk HIT",
        type=str,
        required=True
    )

    args = parser.parse_args()
    file_id = args.id
    hittypeid = args.hittype
    hitlayout = args.hitlayout

    # (1). Retrieve the urls from the app script

    # retrieve gdrive service
    service = get_drive_service()

    # download the most recent forms_urls
    download_forms_urls(URL_INDEX_PATH,file_id,service)
    forms_url = pd.read_csv(URL_INDEX_PATH,sep=r"\s+",header=None,names=['url'],index_col=0)

    # (2). Link to AWS Mturk

    # retrieval of the access keys
    aws_access_key_id,aws_secret_access_key = read_access_keys(AWS_KEYS_PATH)

    # creation of an mturk client
    client = create_mturk_client(aws_access_key_id,aws_secret_access_key)
    myhit = client.create_hit_with_hit_type(
                HITTypeId=hittypeid,
                HITLayoutId=hitlayout,
                HITLayoutParameters = [{'Name':'url',
                           'Value':'https://forms.gle/XKVGkivEhe2JwuEW7'}],
                LifetimeInSeconds = 3600,
                )



