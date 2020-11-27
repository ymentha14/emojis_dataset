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


def get_answer(answer):
        xml_doc = xmltodict.parse(answer)
        return xml_doc['QuestionFormAnswers']['Answer']['FreeText']

class MTurkparam():
    def __init__(self,
                n_forms,
                hitlayout="3VQCRCGMCT2NU7RBSKK6J2PIFKVQ77",
                MaxAssignments = 10,
                LifetimeInSeconds = 600,
                AutoApprovalDelayInSeconds=600,
                AssignmentDurationInSeconds=600,
                Reward='0.01',):
        """
        Args:
            hitlayout (str): hitlayout of the template to use
            lifetimeinsec (int): lifetime in seconds
        """
        self.MaxAssignments = MaxAssignments
        self.hitlayout = hitlayout
        self.LifetimeInSeconds = LifetimeInSeconds
        self.AutoApprovalDelayInSeconds = AutoApprovalDelayInSeconds
        self.AssignmentDurationInSeconds = AssignmentDurationInSeconds
        self.Reward = Reward
        self.n_forms = n_forms
        self.cost = self.MaxAssignments * float(self.Reward) * self.n_forms
        print(f"Estimated cost:{self.cost:.2f} $")
    def __repr__(self):
        return (f"MaxAss:{self.MaxAssignments} Lifetime:{self.LifetimeInSeconds} "
                 +f"Autoapprov:{self.AutoApprovalDelayInSeconds} Reward:{self.Reward} "
                +f"AssignDuration:{self.AssignmentDurationInSeconds}")


class Turker():
    def __init__(self,param,
                    gservice,
                    formidx2url,
                    formidx2gid,
                    formrespath,
                    production=False,):
        """
        Args:
            hittypeid (str): hittypeid of the template to use

        """
        self.p = param
        self.watcher_process = None
        self.gservice = gservice
        self.formidx2url = formidx2url
        self.formidx2gid = formidx2gid
        self.formrespath = Path(formrespath)
        self.production = production

        # retrieval of the access keys
        aws_access_key_id,aws_secret_access_key = read_access_keys(AWS_KEYS_PATH)
        self.client = create_mturk_client(aws_access_key_id,aws_secret_access_key,production)

        # creation of an self.client client
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

    def create_forms_hits(self):
        """

        """
        for idx,url in self.formidx2url.items():
            print(f"Creating hit for form {idx}")

            myhit = self.client.create_hit(
                        MaxAssignments=self.p.MaxAssignments,
                        LifetimeInSeconds = self.p.LifetimeInSeconds,
                        AutoApprovalDelayInSeconds=self.p.AutoApprovalDelayInSeconds,
                        AssignmentDurationInSeconds=self.p.AssignmentDurationInSeconds,
                        Reward=self.p.Reward,
                        HITLayoutId=self.p.hitlayout,
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

    def get_results(self,id):
        """
        id (str or int): worker_id or form_idx
        """
        if type(id) == str:
            assert(id in self.hit2form.keys())
            id = self.hit2form[id]
        path = self.formrespath.joinpath(f"{id}.csv")
        gid = self.formidx2gid[id]
        download_drive_spreadsheet(path,gid,self.gservice,verbose=True)
        df = pd.read_csv(path)
        return df

    def list_assignments(self,hit_id):
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
            df = pd.DataFrame(df)
            return df
        else:
            print(f"No results ready yet for {hit_id}")

    def list_all_assignments(self):
        df = []
        hits = self.client.list_hits()['HITs']
        if len(hits) == 0:
            print("No results")
            return None
        for hit in hits:
            hit_id = hit['HITId']
            df.append(self.list_assignments(hit_id))
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

    def approve_correct_assignments(self,hit_id,dry_run = False):
        """
        Args:
            correct_hits (Bool): whether to correct correct hits exclusively
        """
        form_idx = self.hit2form[hit_id]
        form_path = FORMS_RESULTS_DIR.joinpath(f"{form_idx}.csv")
        form_df = pd.read_csv(form_path)

        assignments = self.client.list_assignments_for_hit(HITId=hit_id,AssignmentStatuses=['Submitted'])
        assignments = assignments['Assignments']

        # Real MTurk worker ids
        workers = set([assignment['WorkerID'] for assignment in assignments])
        password_frauders = self.detect_password_frauders(assignments=assignments,
                                                            password = generate_password(form_idx))

        # Manually entered MTurk ids
        honey_frauders = detect_honey_frauders(form_df,HONEYPOTS) # wrong honeypot
        repeat_frauders = detect_repeat_frauders(form_df) # repeat words
        fakeid_frauders = workers - set(form_df['Worker ID'].unique().tolist()) # workers who entered a fake id

        frauders = (password_frauders.union(honey_frauders)
                                    .union(repeat_frauders)
                                    .union(fakeid_frauders))

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

                if worker_id in fakeid_frauders:
                    RequesterFeedback = "Wrong worker id. \n"

                print(f"Reject assid {ass_id}  wid {worker_id} hitid {hit_id} formidx {form_idx}")
                print(RequesterFeedback)
                if not dry_run:
                    self.client.reject_assignment(AssignmentId=ass_id,
                                                RequesterFeedback=RequesterFeedback)
            else:
                print(f"Approve assid {ass_id}  wid {worker_id} hitid {hit_id} formidx {form_idx}")
                if not dry_run:
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

    def approve_correct_hits(self,dry_run=False):
        hits = self.client.list_reviewable_hits()['HITs']
        for hit in hits:
            self.approve_correct_assignments(hit['HITId'],dry_run)

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

    # download the most recent formidx2urls
    download_formidx2urls(URL_INDEX_PATH,file_id,service)
    formidx2url = pd.read_csv(URL_INDEX_PATH,sep=r"\s+",header=None,names=['url'],index_col=0)

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



