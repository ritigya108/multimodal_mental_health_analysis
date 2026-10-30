/**
 * Mock dashboard data — single source of truth for the Dashboard while the
 * real backend endpoint is not yet wired up.
 *
 * TO SWAP FOR REAL DATA:
 *   In Dashboard.js find the line:
 *       import { MOCK_DASHBOARD } from '../mock/dashboardData';
 *   Replace the `loadDashboard()` body with a real apiService call and remove
 *   that import. Everything else (state shape, component props) stays the same.
 */

export const MOCK_DASHBOARD = {
  /**
   * Latest assessment result — drives KPI cards, risk meter, modality bars,
   * question tiles and key insights.
   */
  latestResult: {
    id: 'assess-0001',
    timestamp: '2026-10-28T14:32:00Z',
    risk_level: 'moderate',          // 'low' | 'moderate' | 'elevated' | 'high'
    confidence: 0.74,                // 0–1
    input_type: 'audio + text',
    demo_mode: false,

    modality_contributions: {
      text:  61.4,                   // percentage (0–100)
      audio: 38.6,
    },
    per_modality_confidence: {
      text:  0.78,
      audio: 0.68,
    },

    /**
     * EATD-Corpus has three emotional-question slots:
     *   positive, neutral, negative
     */
    question_responses: {
      positive: { label: 'Positive',  score: 6.2, max: 10, note: 'Recall a pleasant memory' },
      neutral:  { label: 'Neutral',   score: 5.1, max: 10, note: 'Describe your daily routine' },
      negative: { label: 'Negative',  score: 4.3, max: 10, note: 'Recall a difficult experience' },
    },

    key_findings: [
      'Text analysis detected low positive-affect vocabulary consistent with mild depressive presentation.',
      'Audio prosody (F0 range, speech rate) indicates reduced emotional expressiveness.',
      'Response to the neutral question showed the least divergence from a non-depressed baseline.',
    ],

    sds_estimated: 46,               // PHQ/SDS proxy score (0–80); null if unavailable
  },

  /**
   * Full assessment history — drives the "Recent assessments" table.
   * Add or remove rows here; the table always shows 5 per page.
   */
  assessments: [
    {
      id: 'assess-0001',
      timestamp: '2026-10-28T14:32:00Z',
      risk_level: 'moderate',
      confidence: 0.74,
      input_type: 'audio + text',
    },
    {
      id: 'assess-0002',
      timestamp: '2026-10-21T10:15:00Z',
      risk_level: 'elevated',
      confidence: 0.81,
      input_type: 'audio + text',
    },
    {
      id: 'assess-0003',
      timestamp: '2026-10-14T09:00:00Z',
      risk_level: 'moderate',
      confidence: 0.69,
      input_type: 'text only',
    },
    {
      id: 'assess-0004',
      timestamp: '2026-10-07T16:45:00Z',
      risk_level: 'low',
      confidence: 0.83,
      input_type: 'audio + text',
    },
    {
      id: 'assess-0005',
      timestamp: '2026-09-30T11:20:00Z',
      risk_level: 'low',
      confidence: 0.77,
      input_type: 'text only',
    },
    {
      id: 'assess-0006',
      timestamp: '2026-09-22T08:55:00Z',
      risk_level: 'moderate',
      confidence: 0.72,
      input_type: 'audio + text',
    },
  ],
};
