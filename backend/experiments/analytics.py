from experiments.models import Animal, Session, Trial, DataPoint


def get_overall_session_performance(session_id):
	all_trials = Trial.objects.filter(session_id=session_id)

	trial_count = all_trials.count()
	hits = all_trials.filter(is_licked=True, contrast__gt=0).count()
	false_alarms = all_trials.filter(is_licked=True, contrast=0).count()

	return {
		'trial_count': trial_count,
		'hits': hits/trial_count,
		'false_alarms': false_alarms/trial_count,
	}