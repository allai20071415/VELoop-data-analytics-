# data/raw
Place the two supplied simulated workbooks here (they are not committed, because they contain simulated personal fields such as names and emails and belong to the company pack):

- `1793188481774_VELoop_Rewards_Data_01.xlsx`
- `1793188525986_VELOOP_Simulated_User_Behavior_1000.xlsx`

Then run `python run.py all` and `python -m pytest -q tests` (data-dependent tests are skipped automatically if the files are missing).
