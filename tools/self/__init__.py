from tools.self.file_scanner import (
    auto_index_on_startup, scan_and_report, get_file_content,
)
from tools.self.evo_analyzer import (
    observe_and_signal, generate_proposals_from_signals,
    approve_and_execute, reject_proposal,
    list_proposals, list_reports,
)
from tools.self.importance_scorer import (
    score_query, get_loom_threshold,
    get_repeated_errors, get_scorer_stats,
)
from tools.self.performance_evaluator import (
    record_query, run_evaluation,
    get_current_metrics, get_eval_history,
)
from tools.self.self_learner import (
    learn_topic, learn_from_errors, continuous_learn,
)
