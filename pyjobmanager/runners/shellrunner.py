import logging
import subprocess
import abc
import json
import sys
import datetime
from click import progressbar

#import runner
from pyjobmanager.pypedreamstatus import PypedreamStatus

__author__ = 'vinaykaikala'


class Runner(object):
    """ An abstract class that can run scripts on the cli or submit to a queue.
        Concrete implementations of Runner have to implement the run() method which runs the jobs.
        The pipeline is responsible for generating a list of ordered jobs to run.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def run(self, pipeline):
        pass

    @abc.abstractmethod
    def get_job_status(self, jobid):
        pass




def get_job_name(job):
    if job is not None:
        return job.get_name()
    else:
        return "Done!"


class Shellrunner(Runner):
    def __init__(self):
        self.pipeline = None

    def run(self, pipeline):
        """
        Run the submitted pipeline
        :param pipeline:
        :return: True if no errors occurred, False otherwise
        """
        self.pipeline = pipeline
        ordered_jobs = self.pipeline._get_ordered_jobs_to_run()

        # ordered_jobs = pipeline._get_ordered_jobs()
        with progressbar(ordered_jobs, item_show_func=get_job_name) as bar:
            for job in bar:
                logging.debug("Running {} with script {}".format(job.get_name(), job.script))
                cmd = ["bash", job.script]
                logfile = open(job.log, 'w')
                logging.debug("writing to log {}".format(job.log))
                job.status = PypedreamStatus.RUNNING
                job.starttime = datetime.datetime.now().isoformat()
                proc = None
                try:
                    proc = subprocess.check_call(cmd, stdout=logfile, stderr=logfile)
                    job.endtime = datetime.datetime.now().isoformat()
                    job.complete()
                except subprocess.CalledProcessError as err:
                    job.endtime = datetime.datetime.now().isoformat()
                    job.fail()
                    self.pipeline._write_jobdb_json(ordered_jobs)
                    logfile.flush()
                    with open(job.log, 'r') as logf:
                        logging.warning("Task {} failed with exit code {}".format(job.get_name(),
                                                                                  err.returncode))
                        logging.warning("Contents of " + job.log + ":")
                        logging.warning(logf.read())
                    return err.returncode

                self.pipeline._cleanup()
                self.pipeline._write_jobdb_json(ordered_jobs)
                logfile.close()

        return 0

    def get_job_status(self, jobid):
        return self.pipeline._get_job_with_id(jobid).status
