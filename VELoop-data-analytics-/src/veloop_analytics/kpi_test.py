"""Work Package J3: which proposed KPIs can be calculated from the supplied structure."""
KPI_TEST_COLUMNS = ["kpi", "name", "calculable", "fields_used_or_missing", "dataset", "limitation_or_data_required"]
KPI_TEST = [
 ("K01-K02","Registrations (by source)","YES","registration_datetime, acquisition_source","users","Needs one master users table"),
 ("K03-K05","DAU / WAU / MAU","YES (proxy)","sessions or feature events","B","Qualifying-event list still to be defined"),
 ("K04","Returning users","YES","registration + sessions","B",""),
 ("K06","Onboarding completion rate","PARTIAL","onboarding_status","users","Snapshot only; no onboarding events or timestamps"),
 ("K07","Inactive users","YES","last_login / sessions","users, B","As-of date undocumented"),
 ("K09","Time to first activity","YES","registration + first session","B",""),
 ("K10","Account status distribution","YES","account_status","users","No status history"),
 ("K11-K13","Task starts / completions / completion rate","YES","task_status, task_started_at","B tasks","No validation_status; 648 Pending"),
 ("K14","Failure rate by category","PARTIAL","failure_reason","B tasks","Reasons contradict status in some rows"),
 ("K15-K17","Feature usage / adoption / repeat","YES","feature_name, events","B events",""),
 ("K18-K20,K23","Reward transactions / amounts / by feature","NO","reward amount, unit, reward_id","-","Only reward_status; counts of credited tasks possible, amounts not"),
 ("K21-K22","Reversal rate / pending rewards","PARTIAL","reward_status=Pending","B tasks","No reversal state"),
 ("K24","Activity-to-credit rate","YES (count only)","task_status vs reward_status","B tasks","Credited equals Completed in every row"),
 ("K25-K29","Wallet KPIs and reconciliation","NO","wallet transactions","-","No ledger table; only wallet_viewed events"),
 ("K30-K38","Withdrawal KPIs","NO","withdrawals table","-","Not supplied"),
 ("K39-K42","Referral funnel","NO","referral records","-","Only referral_code and referral events; no referrer/referred link"),
 ("K43-K45","Support KPIs","NO","tickets, help events","-","Not supplied"),
 ("K46","Data-quality pass rate","YES","this audit","all",""),
]
