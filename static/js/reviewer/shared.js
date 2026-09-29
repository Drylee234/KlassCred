// ── Reviewer portal — review modal, shared by the dashboard and assignments pages ──
const REVIEW_LOG = 'kc_review_log';                   // sessionStorage: reviews submitted this session (read by reviews.js)
let onReviewed = () => {};                            // each page sets what to refresh after a review is saved

function openReviewModal(id) {
  $('rv_assignment_id').value = id;
  $('rv_label').textContent = '#' + id;
  ['rv_score', 'rv_notes', 'rv_flag_reason'].forEach(f => { $(f).value = ''; });
  $('rv_flagged').value = 'false';
  $('rv_flag_reason_wrap').style.display = 'none';
  $('reviewModalResp').className = 'response-box';
  openModal('reviewModal');
}

const toggleFlagReason = () => {
  $('rv_flag_reason_wrap').style.display = $('rv_flagged').value === 'true' ? 'block' : 'none';
};

function doSubmitReview() {
  const id = $('rv_assignment_id').value, flagged = $('rv_flagged').value === 'true';
  const body = {
    score: parseFloat($('rv_score').value),
    notes: val('rv_notes') || null,
    flagged,
    flag_reason: flagged ? (val('rv_flag_reason') || null) : null,
  };
  return send('POST', `/reviewer/assignments/${id}/review`, body, {
    resp: 'reviewModalResp', msg: 'Review submitted',
    done: () => {
      const log = JSON.parse(sessionStorage.getItem(REVIEW_LOG) || '[]');
      log.unshift({ assignmentId: id, ...body, at: new Date().toISOString() });
      sessionStorage.setItem(REVIEW_LOG, JSON.stringify(log));
      closeModal('reviewModal');
      onReviewed();
    },
  });
}
