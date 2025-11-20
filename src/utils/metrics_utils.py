from typing import Dict, List
import evaluate


def build_cer_wer_metrics():
    cer_metric = evaluate.load("cer")
    wer_metric = evaluate.load("wer")

    def compute(pred_str: List[str], label_str: List[str]) -> Dict[str, float]:
        cer = cer_metric.compute(predictions=pred_str, references=label_str)
        wer = wer_metric.compute(predictions=pred_str, references=label_str)
        return {"cer": cer, "wer": wer}

    return compute
