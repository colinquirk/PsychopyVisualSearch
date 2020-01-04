# Psychopy Visual Search

A basic T and L visual search experiment.

Author - Colin Quirk (cquirk@uchicago.edu)

T and L visual search is a common attention paradigm. Unlike other visual search tasks, this task
forces participants to search serially, resulting in increasing RT with set size
(e.g. Wolfe, Cave, Franzel, 1989). If `visualsearch.py` is run directly, the defaults at the top of the
file will be used. To make simple changes, you can adjust any of these values. For more in depth
changes you will need to overwrite the methods yourself.

**Note**: this code relies on my templateexperiments module. You can get it from
[https://github.com/colinquirk/templateexperiments](https://github.com/colinquirk/templateexperiments) and either put it in the same folder as this
code or give the path to psychopy in the preferences.

## Classes
TLTask -- The class that runs the experiment.

#### Parameters
- allowed_deg_from_fix -- The maximum distance in visual degrees the stimuli can appear from
    fixation
- data_directory -- Where the data should be saved.
- instruct_text -- The text to be displayed to the participant at the beginning of the
    experiment.
- iti_time -- The number of seconds in between a response and the next trial.
- keys -- The keys to be used for making a response. Should match possible_orientations.
- max_per_quad -- The number of stimuli allowed in each quadrant. If None, displays are
    completely random. Useful for generating more "spread out" displays
- min_distance -- The minimum distance in visual degrees between stimuli.
- number_of_blocks -- The number of blocks in the experiment.
- number_of_trials_per_block -- The number of trials within each block.
- possible_orientations -- A list of strings possibly including "left", "up", "right", or "down"
- questionaire_dict -- Questions to be included in the dialog.
- set_sizes -- A list of all the set sizes. An equal number of trials will be shown for each set
    size.
- stim_path -- A string containing the path to the stim folder
- stim_size -- The size of the stimuli in visual angle.

Additional keyword arguments are sent to template.BaseExperiment().

#### Methods
- chdir -- Changes the directory to where the data will be saved.
- display_break -- Displays a screen during the break between blocks.
- display_blank -- Displays a blank screen.
- display_search -- Displays the search array.
- generate_locations -- Helper function that generates locations for make_trial
- get_response -- Waits for a response from the participant.
- make_block -- Creates a block of trials to be run.
- make_trial -- Creates a single trial.
- run_trial -- Runs a single trial.
- run -- Runs the entire experiment.
- send_data -- Updates the experiment data with the information from the last trial.
