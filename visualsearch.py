import errno
import json
import os
import random
import sys

import numpy as np

import psychopy.core
import psychopy.event
import psychopy.visual

import template

# Things you probably want to change
exp_name = 'VisualSearch'

number_of_trials_per_block = 10
number_of_blocks = 5

set_sizes = [2, 6, 10, 14, 18]

instruct_text = [
    ('Welcome to the experiment. Press space to begin.'),
    ('In this experiment you will be searching for "T"s.\n\n'
     'Each trial will start with a fixation cross. '
     'Then, 6 items will appear.\n\n'
     'One will be a "T" and the others will be offset "L"s.\n\n'
     'The "T" can appear in any orientation.\n\n'
     'Once you find the "T", press the arrow key associated with the top of the "T".\n\n'
     'For example, if the "T" looks normal, you would press the up arrow key.\n\n'
     'If the top of the T is pointed to the left, you would press the left arrow key.\n\n'
     'You will get breaks in between blocks.\n\n'
     'Press space to continue.'),
]

data_directory = os.path.join(os.path.expanduser('~'), 'Desktop', exp_name, 'Data')
# Feel free to hardcode to your system if this file will be imported
stim_path = os.path.join(os.getcwd(), 'stim')

# Things you probably don't need to change, but can if you want to
stim_size = 1  # visual degrees, used for X and Y

possible_orientations = ['left', 'up', 'right', 'down']
keys = ['left', 'up', 'right', 'down']  # keys indexes should match with possible_orientations

allowed_deg_from_fix = 6
# minimum euclidean distance between centers of stimuli in visual angle
# min_distance should be greater than stim_size
min_distance = 2
max_per_quad = None  # int or None for totally random displays

iti_time = 1  # seconds

distance_to_monitor = 90  # cm

# data_fields must match input to send_data
data_fields = [
    'Subject',
    'Block',
    'Trial',
    'Timestamp',
    'SetSize',
    'RT',
    'CRESP',
    'RESP',
    'ACC',
    'LocationTested',
    'Locations',
    'Rotations',
    'Stimuli'
]

gender_options = [
    'Male',
    'Female',
    'Other/Choose Not To Respond',
]

hispanic_options = [
    'Yes, Hispanic or Latino/a',
    'No, not Hispanic or Latino/a',
    'Choose Not To Respond',
]

race_options = [
    'American Indian or Alaskan Native',
    'Asian',
    'Pacific Islander',
    'Black or African American',
    'White / Caucasian',
    'More Than One Race',
    'Choose Not To Respond',
]

# Add additional questions here
questionaire_dict = {
    'Age': 0,
    'Gender': gender_options,
    'Hispanic:': hispanic_options,
    'Race': race_options,
}


# This is the logic that runs the experiment
# Change anything below this comment at your own risk
class TLTask(template.BaseExperiment):
    def __init__(self, number_of_trials_per_block=number_of_trials_per_block,
                 number_of_blocks=number_of_blocks, set_sizes=set_sizes, stim_size=stim_size,
                 possible_orientations=possible_orientations, keys=keys,
                 allowed_deg_from_fix=allowed_deg_from_fix, min_distance=min_distance,
                 max_per_quad=max_per_quad, instruct_text=instruct_text, iti_time=iti_time,
                 data_directory=data_directory, questionaire_dict=questionaire_dict, **kwargs):

        self.number_of_trials_per_block = number_of_trials_per_block
        self.number_of_blocks = number_of_blocks

        self.set_sizes = set_sizes

        self.stim_size = stim_size

        self.possible_orientations = possible_orientations
        self.keys = keys

        if len(self.keys) != len(self.possible_orientations):
            raise ValueError('Length of keys and possible_orientations must be equal.')

        self.allowed_deg_from_fix = allowed_deg_from_fix
        self.min_distance = min_distance
        self.max_per_quad = max_per_quad

        self.instruct_text = instruct_text

        self.iti_time = iti_time

        self.data_directory = data_directory
        self.questionaire_dict = questionaire_dict
        self.T_stim_path = os.path.join(os.getcwd(), 'stim/T.png')
        self.L1_stim_path = os.path.join(os.getcwd(), 'stim/L1.png')
        self.L2_stim_path = os.path.join(os.getcwd(), 'stim/L2.png')

        self.trials_per_set_size = number_of_trials_per_block / len(set_sizes)

        if self.trials_per_set_size % 1 != 0:
            raise ValueError('number_of_trials_per_block must be divisible by len(set_sizes).')

        self.trials_per_set_size = int(self.trials_per_set_size)

        super().__init__(**kwargs)

    def chdir(self):
        """Changes the directory to where the data will be saved."""

        try:
            os.makedirs(self.data_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        os.chdir(self.data_directory)

    def make_block(self):
        trial_list = []

        for set_size in self.set_sizes:
            for _ in range(self.trials_per_set_size):
                trial = self.make_trial(set_size)
                trial_list.append(trial)

        random.shuffle(trial_list)

        return trial_list

    @staticmethod
    def _which_quad(loc):
        """Checks which quad a location is in.
        This method is used by generate_locations to ensure the max_per_quad condition is followed.
        Parameters:
        loc -- A list of two values (x,y) in visual angle.
        """
        if loc[0] < 0 and loc[1] < 0:
            return 0
        elif loc[0] >= 0 and loc[1] < 0:
            return 1
        elif loc[0] < 0 and loc[1] >= 0:
            return 2
        else:
            return 3

    def _too_close(self, attempt, locs):
        """Checks that an attempted location is valid.
        This method is used by generate_locations to ensure the min_distance condition is followed.
        Parameters:
        attempt -- A list of two values (x,y) in visual angle.
        locs -- A list of previous successful attempts to be checked.
        """
        if np.linalg.norm(np.array(attempt)) < self.min_distance:
            return True  # Too close to center

        for loc in locs:
            if np.linalg.norm(np.array(attempt) - np.array(loc)) < self.min_distance:
                return True  # Too close to another square

        return False

    def generate_locations(self, set_size):
        if self.max_per_quad is not None:
            # quad boundries (x1, x2, y1, y2)
            quad_count = [0, 0, 0, 0]

        locs = []
        counter = 0
        while len(locs) < set_size:
            counter += 1
            if counter > 1000:
                raise ValueError('Timeout -- Cannot generate locations with given values.')

            attempt = [random.uniform(-self.allowed_deg_from_fix, self.allowed_deg_from_fix)
                       for _ in range(2)]

            if self._too_close(attempt, locs):
                continue

            if self.max_per_quad is not None:
                quad = self._which_quad(attempt)

                if quad_count[quad] < self.max_per_quad:
                    quad_count[quad] += 1
                    locs.append(attempt)
            else:
                locs.append(attempt)

        return locs

    def make_trial(self, set_size):
        test_location = random.randint(0, set_size - 1)

        locs = self.generate_locations(set_size)

        ori_idx = [random.randint(0, len(self.possible_orientations) - 1) for _ in range(set_size)]
        oris = [self.possible_orientations[i] for i in ori_idx]

        replacement_orientations = {
            'left': 270,
            'up': 0,
            'right': 90,
            'down': 180
        }

        oris = [replacement_orientations[ori] for ori in oris]
        cresp = self.keys[ori_idx[test_location]]

        stims = [random.choice(['L1', 'L2']) for _ in range(set_size)]
        stims[test_location] = 'T'

        trial = {
            'set_size': set_size,
            'cresp': cresp,
            'locations': locs,
            'rotations': oris,
            'stimuli': stims,
            'test_location': test_location,
        }

        return trial

    def display_break(self):
        """Displays a break screen in between blocks."""

        break_text = 'Please take a short break. Press space to continue.'
        self.display_text_screen(text=break_text, bg_color=[204, 255, 204])

    def display_blank(self, wait_time):
        """Displays a fixation cross. A helper function for self.run_trial.
        Parameters:
        wait_time -- The amount of time the fixation should be displayed for.
        """

        self.experiment_window.flip()

        psychopy.core.wait(wait_time)

    def display_search(self, coordinates, rotations, stimuli):

        for pos, ori, stim in zip(coordinates, rotations, stimuli):
            if stim == "T":
                path = self.T_stim_path
            elif stim == "L1":
                path = self.L1_stim_path
            else:
                path = self.L2_stim_path

            psychopy.visual.ImageStim(self.experiment_window, image=path, pos=pos, ori=ori,
                                      size=self.stim_size).draw()

        self.experiment_window.flip()

    def get_response(self, allow_quit=True):
        """Waits for a response from the participant. A helper function for self.run_trial.
        Pressing Q while the function is wait for a response will quit the experiment.
        Returns the pressed key and the reaction time.
        """

        rt_timer = psychopy.core.MonotonicClock()

        keys = self.keys
        if allow_quit:
            keys += ['q']

        resp = psychopy.event.waitKeys(keyList=keys, timeStamped=rt_timer)

        if 'q' in resp[0]:
            self.quit_experiment()

        return resp[0][0], resp[0][1]*1000  # key and rt in milliseconds

    def send_data(self, data):
        """Updates the experiment data with the information from the last trial.
        This function is seperated from run_trial to allow additional information to be added
        afterwards.
        Parameters:
        data -- A dict where keys exist in data_fields and values are to be saved.
        """
        self.update_experiment_data([data])

    def run_trial(self, trial, block_num, trial_num):
        """Runs a single trial.
        Returns the data from the trial after getting a participant response.
        Parameters:
        trial -- The dictionary of information about a trial.
        block_num -- The number of the block in the experiment.
        trial_num -- The number of the trial within a block.
        """
        self.display_blank(self.iti_time)
        self.display_search(trial['locations'], trial['rotations'], trial['stimuli'])

        resp, rt = self.get_response()

        acc = 1 if resp == trial['cresp'] else 0

        data = {
            'Subject': self.experiment_info['Subject Number'],
            'Block': block_num,
            'Trial': trial_num,
            'Timestamp': psychopy.core.getAbsTime(),
            'SetSize': trial['set_size'],
            'RT': rt,
            'CRESP': trial['cresp'],
            'RESP': resp,
            'ACC': acc,
            'LocationTested': trial['test_location'],
            'Locations': json.dumps(trial['locations']),
            'Rotations': json.dumps(trial['rotations']),
            'Stimuli': str(trial['stimuli']),  # avoids double quotes issues
        }

        return data

    def run(self):
        """Runs the entire experiment if the file is run directly."""

        self.chdir()

        ok = self.get_experiment_info_from_dialog(self.questionaire_dict)

        if not ok:
            print('Experiment has been terminated.')
            sys.exit(1)

        self.save_experiment_info()
        self.open_csv_data_file()
        self.open_window(screen=0)
        self.display_text_screen('Loading...', wait_for_input=False)

        for instruction in self.instruct_text:
            self.display_text_screen(text=instruction)

        for block_num in range(self.number_of_blocks):
            block = self.make_block()
            for trial_num, trial in enumerate(block):
                data = self.run_trial(trial, block_num, trial_num)
                self.send_data(data)

            self.save_data_to_csv()

            if block_num + 1 != self.number_of_blocks:
                self.display_break()

        self.display_text_screen(
            'The experiment is now over, please get your experimenter.',
            bg_color=[0, 0, 255], text_color=[255, 255, 255])

        self.quit_experiment()


if __name__ == "__main__":
    exp = TLTask(
        # BaseExperiment parameters
        experiment_name=exp_name,
        data_fields=data_fields,
        monitor_distance=distance_to_monitor,
        # Custom parameters go here
    )

    exp.run()
