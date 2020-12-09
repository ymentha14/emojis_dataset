
from src.data.auto_mturk import create_mturk_client
from src.utils import  read_access_keys
from src.data.auto_drive import download_all_csv_results,get_drive_service
import pandas as pd
from IPython.display import clear_output
from time import sleep
from botocore.exceptions import ClientError
from src.constants import AWS_KEYS_PATH,WATCHER_FORMS_RESULTS_DIR
import argparse
from src.utils import get_form_urls

class Watcher():
    """g
    Class to monitor the workers who complete more than a defined max_forms
    of our tasks ==> tag them to prevent them from keeping answering
    """
    def __init__(self,form_results_dir,
                    formidx2gid,
                    drive_service,
                    max_forms=2,
                    production=False):
        """
        Args:
            form_results_dir (pathlib Path): directory where to store the forms csv to analyze
            formidx2gid (dict): mapping between form idx and google drive id for results
            drive_service: as returned by get_drive_service.get_drive_service
            max_forms (int): maximum number of forms a worker is allowed to complete
            production (Bool): sandbox if set to false
        """
        self.production = production
        # retrieval of the access keys
        aws_access_key_id,aws_secret_access_key = read_access_keys(AWS_KEYS_PATH)
        # creation of an self.client client
        self.client = create_mturk_client(aws_access_key_id,aws_secret_access_key,production)
        self.max_forms = max_forms
        self.form_results_dir = form_results_dir
        self.formidx2gid = formidx2gid
        self.drive_service = drive_service

    def get_workers2tag(self):
        """
        Return the set of workerid that need to get tagged
        """
        download_all_csv_results(self.formidx2gid,
                                self.form_results_dir,
                                self.drive_service)
        meta_df = []
        for form_path in self.form_results_dir.iterdir():
            df = pd.read_csv(form_path,usecols=['Worker ID'])
            meta_df.append(df)
        meta_df = pd.concat(meta_df,axis=0)
        # number of different
        forms_count = meta_df['Worker ID'].value_counts()
        forms_count = forms_count[forms_count >= self.max_forms]
        return set(forms_count.index.tolist())

    def get_tagged_workers(self,qualification_type_id):
        """
        Return the set of Workerid that are already tagged
        """
        # search for workers already tagged
        exworkers = set()
        qualifs = self.client.list_workers_with_qualification_type(QualificationTypeId=qualification_type_id)
        for qualif in qualifs['Qualifications']:
            if qualif['QualificationTypeId'] == qualification_type_id:
                exworkers.add(qualif['WorkerId'])
        return exworkers

    def monitor(self,qualification_type_id):
        """
        Function to run in a separate thread: check periodically for new workers to tag
        """
        # search for workers already tagged
        i = 0
        while True:
            print(f"{i} th iteration")
            # information comes from google drive
            tagged_workers = self.get_tagged_workers(qualification_type_id)
            workers2tag = self.get_workers2tag()
            # remove the workers already tagged
            workers2tag = workers2tag - tagged_workers

            print("Tagged workers:",end="")
            for workerid in tagged_workers:
                print(f"{workerid},")

            for workerid in workers2tag:
                print(f"Tagging worker {workerid}")
                # TODO: do a try except to catch a wrongly typed workerid
                try:
                    self.client.associate_qualification_with_worker(
                        QualificationTypeId=qualification_type_id,
                        WorkerId=workerid,
                        IntegerValue=1,
                        SendNotification=False
                    )
                except ClientError:
                    print(f"Non valid worker id {workerid}")
            clear_output(wait=True)
            i+=1
            sleep(12)

    def clean_all_workers(self,qualification_type_id):
        workers = self.get_tagged_workers(qualification_type_id)
        for wid in workers:
            self.client.disassociate_qualification_from_worker(
            WorkerId=wid,
            QualificationTypeId=qualification_type_id,
            Reason='First pilot terminated, you can answer the next pilots'
        )
        print(f"All workers cleaned! ({workers})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--id',
        help="id of the files index",
        type=str
    )
    parser.add_argument(
        '--qualifid',
        help="id of the qualification to watch for",
        type=str
    )
    
    parser.add_argument(
        '--max_forms',
        help="maximum number of forms",
        type=int
    )
    parser.add_argument(
        '--production',
        help="production or not",
        type=bool,
        default=False
    )
    args = parser.parse_args()
    file_id = args.id
    max_forms = args.max_forms
    qualifid = args.qualifid
    service = get_drive_service()

    formidx2url,formidx2gid = get_form_urls(service,file_id)

    watcher = Watcher(form_results_dir=WATCHER_FORMS_RESULTS_DIR,
                  formidx2gid=formidx2gid,
                  drive_service=service,
                  max_forms=max_forms,
                  production=args.production)
    watcher.monitor(qualification_type_id = qualifid)
