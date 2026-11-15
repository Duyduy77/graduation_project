const signature = profile => profile ? JSON.stringify(Object.entries(profile.features).sort(([a],[b]) => a.localeCompare(b))) : null;

export function referencePresentation(result) {
  if (!result?.predicted_phone) return {kind:'target',title:'Target reference',note:''};
  const feedback=result.articulation_feedback;
  const sameShape=result.predicted_phone===result.target_phone || (feedback &&
    feedback.observed_reference.family===feedback.target_reference.family &&
    signature(feedback.observed_reference)===signature(feedback.target_reference));
  if(sameShape){
    if(result.predicted_phone===result.target_phone)return {kind:'shared',title:'Target reference',note:''};
    const labels=`Model /${result.predicted_phone}/ · target /${result.target_phone}/.`;
    const lengthUnknown=result.predicted_phone!==result.target_phone && feedback?.target_reference.family==='vowel';
    return {kind:'shared',title:'Shared mouth-shape reference',note:labels+' '+(lengthUnknown?
      'Both labels use the same illustrated shape. Vowel length has not been assessed; no length error is established.':
      'These labels use one illustrated shape. This is a reference, not a measurement of your mouth.')};
  }
  if(result.details?.unresolved_reason==='notation_or_length')return {
    kind:'target',title:'Target reference',note:'The model labels do not establish a mouth-shape correction here. Use the target as a practice reference.'};
  return {kind:'contrast',title:'Target sound: reference position',note:''};
}

export function quickCue(lesson, phone, result) {
  const quality=result?.details?.audio_quality;
  if(quality && (quality.rms<.003 || quality.clipping_fraction>.01) && result.reasons?.length)return result.reasons[0];
  if(result?.status==='possible_difference' && result.articulation_feedback?.differences.length){
    const differences=result.articulation_feedback.differences;
    const next=['lip_shape','place','tongue_height','tongue_region','airflow','voicing'].map(name=>differences.find(d=>d.dimension===name)).find(Boolean);
    return (next || differences[0]).adjustment;
  }
  if(result?.status==='model_match')return `Keep that comfortable shape and say “${lesson.word}” once more.`;
  if(result?.status==='uncertain')return `Try “${lesson.word}” once at a comfortable pace.`;
  return lesson.quick_cue || lesson.steps[1].text;
}
