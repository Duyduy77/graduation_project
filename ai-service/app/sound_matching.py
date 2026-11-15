"""Locate a focal label using surrounding sounds, independently of its target."""
from .sound_catalog import GUIDES, VOWEL_FEATURES, practice_cue, articulation_feedback

# Recognize nucleus positions without requiring the intended vowel. Unsupported
# diphthongs still count as nuclei, but never receive fabricated monophthong guides.
NUCLEI = set(VOWEL_FEATURES) | {"eɪ", "aɪ", "ɔɪ", "oʊ", "əʊ", "aʊ", "ɚ", "ɝ", "ɜː", "ɒ", "y", "ɨ", "ø", "œ"}


def word_candidate(phones, family):
    nuclei = [index for index, phone in enumerate(phones) if phone in NUCLEI]
    if len(nuclei) != 1:
        return [], "Word-only mode needs one vowel nucleus. Say only the selected word once, or trim the recording to it."
    nucleus = nuclei[0]
    if family == "vowel":
        return [nucleus], None
    if nucleus == 0:
        return [], "No starting consonant was decoded before the vowel. It may be missing, or the model may have missed it. Try a clear onset, then analyze again."
    # All primary consonant prompts focus on the start of a word. No expected
    # consonant or vowel is used to choose this observed initial token.
    return [0], None


def match_sound(prediction, prompt, input_scope="context"):
    phones = prediction["predicted_phones"]
    before, after = prompt["before"], prompt["after"]
    target = prompt["target_phone"]
    details = {"timing_status": prediction["timing_status"],
               "probability_status": "uncalibrated; experimental gates are not accuracy",
               "reference_transcript_used_by_model": False,
               "guide_status": "generic_reference_not_measured_mouth_position",
               "vowel_duration_assessed": False, "input_scope": input_scope}
    result = {"status": "uncertain", "predicted": None, "raw": phones, "details": details, "practice_cue": None,
              "message": "I could not isolate the requested sound reliably.",
              "reasons": ["Read the suggested phrase once, keeping the complete word and a little surrounding context."],
              "articulation_feedback": None}
    candidates = []
    if input_scope == "word":
        candidates, problem = word_candidate(phones, prompt["family"])
        if problem:
            result["message"] = problem
            result["reasons"] = ["The model has not established a sound substitution; no mouth position is inferred."]
            details["unresolved_reason"] = "isolated_word_structure"
    else:
        for index in range(len(phones)):
            if index < len(before) or index + len(after) >= len(phones):
                continue
            prefix = phones[index - len(before):index]
            suffix = phones[index + 1:index + 1 + len(after)]
            if (all(phone in choices for phone, choices in zip(prefix, before)) and
                    all(phone in choices for phone, choices in zip(suffix, after))):
                candidates.append(index)
    details["candidate_anchor_count"] = len(candidates)
    if len(candidates) != 1:
        return result
    index = candidates[0]
    raw_phone = phones[index]
    # Latin g and IPA script-g are notation variants, not sound corrections.
    phone = "ɡ" if raw_phone == "g" else raw_phone
    details["candidate_model_label"] = raw_phone
    guide = GUIDES.get(phone)
    if not guide or guide["family"] != prompt["family"]:
        result["message"] = f"The model decoded /{raw_phone}/ here; this sound does not have a supported comparison guide."
        result["reasons"] = ["The raw prediction is retained below. A mouth-position estimate for an unsupported label would be a guess."]
        details["unresolved_reason"] = "unsupported_sound_category"
        return result
    span = prediction["spans"][index]
    details["approximate_target_sound_span"] = [span["start_seconds"], span["end_seconds"]]
    details["word_anchor_status"] = ("one_observed_nucleus; selected_by_word_position_not_target_label" if input_scope == "word"
                                     else "one_unique_surrounding_sound_pattern; word alignment is unverified")
    details["target_model_peak_probability_uncalibrated"] = span["mean_frame_peak_probability"]
    if span["mean_frame_peak_probability"] < 0.6:
        result["predicted"] = phone
        result["articulation_feedback"] = articulation_feedback(phone, target, evidence="weak_model_hypothesis")
        result["message"] = f"A tentative candidate is /{phone}/; the evidence is weak, so a pronunciation error is not confirmed."
        result["reasons"] = ["Listen to your recording before using this candidate's reference. Try recording the word once more."]
        details["unresolved_reason"] = "weak_acoustic_evidence"
        return result
    # A CTC emission run is not phoneme duration. Do not infer vowel length or
    # reject a valid label just because its emission is a single frame.
    result["predicted"] = phone
    result["articulation_feedback"] = articulation_feedback(phone, target)
    if (phone, target) in {("i", "iː"), ("u", "uː"), ("e", "ɛ")}:
        result["message"] = f"The model suggests /{phone}/, but notation or length remains unresolved."
        result["reasons"] = ["Compare the quality references; this output does not establish vowel duration or an accent error."]
        details["unresolved_reason"] = "notation_or_length"
        return result
    matched = phone == target
    result["status"] = "model_match" if matched else "possible_difference"
    result["practice_cue"] = practice_cue(phone, target) if not matched else None
    result["message"] = (f"The model's selected sound matches /{target}/." if matched else
                         f"The model suggests /{phone}/ for the selected sound; the target is /{target}/.")
    result["reasons"] = ["This is an experimental label comparison, not an expert pronunciation grade.",
                         "Only the selected sound is compared; the other sounds in the word are not graded."]
    if prompt["family"] == "vowel":
        result["reasons"].append("Vowel quality is compared; how long you held the vowel is not graded.")
    return result
