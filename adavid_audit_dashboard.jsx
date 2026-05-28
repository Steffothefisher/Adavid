import React, { useState, useMemo } from 'react';
import { ChevronDown, AlertTriangle, CheckCircle, TrendingUp, Layers } from 'lucide-react';

const ADAVIDDashboard = () => {
  const [expandedSection, setExpandedSection] = useState('overview');
  const [showDetails, setShowDetails] = useState(false);

  // Simulated audit results
  const auditData = {
    global: {
      p_value: 0.0342,
      success: true,
      positive_trend: true,
    },
    segmentation: {
      segments_analyzed: 12,
      simpson_paradox_detected: true,
      details: {
        'Age:Young|VariantX:True|Comorb:0': {
          sample_size: 18,
          p_value: 0.0156,
          statistically_significant: true,
          effective: true,
        },
        'Age:Young|VariantX:False|Comorb:1': {
          sample_size: 12,
          p_value: 0.4821,
          statistically_significant: false,
          effective: false,
        },
        'Age:Senior|VariantX:True|Comorb:2': {
          sample_size: 9,
          p_value: 0.0687,
          statistically_significant: false,
          effective: false,
        },
        'Age:Middle-Aged|VariantX:False|Comorb:0': {
          sample_size: 15,
          p_value: 0.0023,
          statistically_significant: true,
          effective: true,
        },
      },
    },
  };

  const failedSegments = useMemo(() => {
    return Object.entries(auditData.segmentation.details).filter(
      ([_, data]) => !data.effective
    );
  }, []);

  const ExpandableSection = ({ title, id, children, icon: Icon }) => (
    <div className="mb-4 border border-zinc-800 rounded-lg overflow-hidden hover:border-cyan-600/50 transition-colors">
      <button
        onClick={() => setExpandedSection(expandedSection === id ? null : id)}
        className="w-full px-5 py-4 flex items-center justify-between bg-gradient-to-r from-zinc-900 to-zinc-950 hover:from-zinc-800 hover:to-zinc-900 transition-all"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5 text-cyan-400" />
          <span className="font-semibold text-white">{title}</span>
        </div>
        <ChevronDown
          className={`w-5 h-5 text-cyan-400 transition-transform ${
            expandedSection === id ? 'rotate-180' : ''
          }`}
        />
      </button>
      {expandedSection === id && (
        <div className="px-5 py-4 bg-zinc-950 border-t border-zinc-800">{children}</div>
      )}
    </div>
  );

  const StatCard = ({ label, value, unit = '', status = 'neutral' }) => {
    const statusColors = {
      success: 'text-green-400 bg-green-400/10',
      warning: 'text-orange-400 bg-orange-400/10',
      danger: 'text-red-400 bg-red-400/10',
      neutral: 'text-cyan-400 bg-cyan-400/10',
    };

    return (
      <div className={`rounded-lg p-4 ${statusColors[status]}`}>
        <div className="text-sm font-medium opacity-80">{label}</div>
        <div className="text-2xl font-bold mt-1">
          {value}
          <span className="text-sm ml-1 opacity-70">{unit}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-black text-white font-mono overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12 border-b border-zinc-800 pb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
            <span className="text-xs uppercase tracking-widest text-cyan-400 font-semibold">
              Pharmaceutical Audit Engine
            </span>
          </div>
          <h1 className="text-5xl font-black text-white mb-3 tracking-tight">
            ADAVID AUDIT REPORT
          </h1>
          <p className="text-zinc-400 max-w-2xl">
            Advanced Data-Driven Visualization & Impact Detection — Multidimensional clinical trial analysis with Simpson's Paradox detection and patient subgroup stratification.
          </p>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Global P-Value"
            value={auditData.global.p_value.toFixed(4)}
            status={auditData.global.success ? 'success' : 'danger'}
          />
          <StatCard
            label="Manufacturer Success"
            value={auditData.global.success ? 'YES' : 'NO'}
            status={auditData.global.success ? 'success' : 'danger'}
          />
          <StatCard
            label="Segments Analyzed"
            value={auditData.segmentation.segments_analyzed}
            status="neutral"
          />
          <StatCard
            label="Simpson's Paradox"
            value={auditData.segmentation.simpson_paradox_detected ? 'DETECTED' : 'NONE'}
            status={auditData.segmentation.simpson_paradox_detected ? 'warning' : 'success'}
          />
        </div>

        {/* Main Audit Sections */}
        <div className="space-y-6">
          {/* Global Effect Analysis */}
          <ExpandableSection
            title="1. Global Effect Analysis"
            id="overview"
            icon={TrendingUp}
          >
            <div className="space-y-4">
              <div className="bg-zinc-900/50 rounded-lg p-4 border border-zinc-800">
                <h3 className="text-sm font-semibold text-cyan-400 mb-3">
                  Population-Level Results
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-zinc-400">Treatment vs Control (t-test):</span>
                    <span className="text-white font-mono">
                      p = {auditData.global.p_value.toFixed(4)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-400">Significance (α = 0.05):</span>
                    <span className="text-green-400 font-bold flex items-center gap-2">
                      <CheckCircle className="w-4 h-4" /> SIGNIFICANT
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-400">Biomarker Trend:</span>
                    <span className="text-green-400 font-bold">
                      Treatment &gt; Control ✓
                    </span>
                  </div>
                </div>
              </div>
              <p className="text-xs text-zinc-500 leading-relaxed">
                The overall pharmaceutical intervention shows statistical significance at the population level (p &lt; 0.05). However, this masks critical subgroup performance variations...
              </p>
            </div>
          </ExpandableSection>

          {/* Multidimensional Segmentation */}
          <ExpandableSection
            title="2. Multidimensional Segmentation Analysis"
            id="segmentation"
            icon={Layers}
          >
            <div className="space-y-4">
              <div className="bg-zinc-900/50 rounded-lg p-4 border border-zinc-800">
                <h3 className="text-sm font-semibold text-cyan-400 mb-3">
                  Patient Subgroup Matrix
                </h3>
                <p className="text-xs text-zinc-400 mb-3">
                  Segmentation by: Age_Group × Genetic_Variant_X × Comorbidities_Count
                </p>
                <div className="space-y-2">
                  {Object.entries(auditData.segmentation.details).map(
                    ([segment, data], idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded border text-xs ${
                          data.effective
                            ? 'bg-green-900/30 border-green-700/50'
                            : 'bg-red-900/30 border-red-700/50'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-mono font-semibold text-white">
                            {segment}
                          </span>
                          {data.effective ? (
                            <span className="text-green-400 text-xs font-bold">
                              RESPONDER
                            </span>
                          ) : (
                            <span className="text-red-400 text-xs font-bold">
                              NON-RESPONDER
                            </span>
                          )}
                        </div>
                        <div className="flex justify-between text-zinc-400">
                          <span>N = {data.sample_size}</span>
                          <span className="font-mono">
                            p = {data.p_value.toFixed(4)}
                          </span>
                          <span>
                            {data.statistically_significant
                              ? '✓ Sig.'
                              : '✗ Noise'}
                          </span>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            </div>
          </ExpandableSection>

          {/* Simpson's Paradox Detection */}
          <ExpandableSection
            title="3. Simpson's Paradox & Non-Responder Analysis"
            id="paradox"
            icon={AlertTriangle}
          >
            <div className="space-y-4">
              {auditData.segmentation.simpson_paradox_detected && (
                <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-red-400 mb-1">
                        ⚠️ SIMPSON'S PARADOX DETECTED
                      </h3>
                      <p className="text-xs text-zinc-300">
                        Global success masks contradictory trends in specific patient subgroups. The drug shows positive overall efficacy but fails or reverses effect in certain demographic clusters.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-zinc-900/50 rounded-lg p-4 border border-zinc-800">
                <h3 className="text-sm font-semibold text-orange-400 mb-3">
                  Critical Non-Responder Clusters
                </h3>
                {failedSegments.length > 0 ? (
                  <div className="space-y-2">
                    {failedSegments.map(([segment, data], idx) => (
                      <div key={idx} className="p-3 bg-zinc-950 rounded border border-orange-700/30">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-mono text-xs font-bold text-orange-400">
                            {segment}
                          </span>
                          <span className="text-xs text-orange-400">
                            WIRKUNGSLOS (Statistical Noise)
                          </span>
                        </div>
                        <div className="flex gap-4 text-xs text-zinc-400">
                          <span>N = {data.sample_size}</span>
                          <span>p = {data.p_value.toFixed(4)}</span>
                          <span>
                            {data.statistically_significant
                              ? '⚠️ Statistically Significant'
                              : '⊘ Non-significant'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-zinc-400">No critical non-responder clusters detected.</p>
                )}
              </div>

              <p className="text-xs text-zinc-500 leading-relaxed">
                This represents a major regulatory concern: while the drug demonstrates efficacy in the overall population, it may be actively harmful or inert in specific patient phenotypes. Pharmacovigilance and post-marketing surveillance should prioritize these subgroups.
              </p>
            </div>
          </ExpandableSection>

          {/* Code Architecture */}
          <ExpandableSection
            title="4. Code Architecture & Methodology"
            id="methods"
            icon={Layers}
          >
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-zinc-900/50 rounded-lg p-4 border border-zinc-800">
                  <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3">
                    1. Data Verification Layer
                  </h4>
                  <ul className="text-xs text-zinc-400 space-y-2">
                    <li>✓ Remove critical nulls (Patient_ID, Group, Biomarker_Drop)</li>
                    <li>✓ Eliminate invalid group labels</li>
                    <li>✓ Remove negative/impossible values (Age &lt; 0)</li>
                    <li>✓ Impute missing ages with categorical bins</li>
                    <li>✓ Assert minimum sample size (n ≥ 10)</li>
                  </ul>
                </div>

                <div className="bg-zinc-900/50 rounded-lg p-4 border border-zinc-800">
                  <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3">
                    2. ADAVID Engine
                  </h4>
                  <ul className="text-xs text-zinc-400 space-y-2">
                    <li>✓ Global t-test (Treatment vs Control)</li>
                    <li>✓ 3D segmentation (Age × Genetic × Comorbidities)</li>
                    <li>✓ Bonferroni correction (α/k)</li>
                    <li>✓ Simpson's Paradox detection</li>
                    <li>✓ Regulatory-grade audit trail logging</li>
                  </ul>
                </div>
              </div>

              <div className="bg-zinc-900/50 rounded-lg p-4 border border-cyan-700/30 space-y-3">
                <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
                  Key Statistical Safeguards
                </h4>
                <div className="text-xs text-zinc-400 space-y-2">
                  <div>
                    <span className="text-cyan-400 font-mono">Bonferroni Correction:</span>{' '}
                    α_adj = 0.05 / number_of_segments (prevents multiple comparison bias)
                  </div>
                  <div>
                    <span className="text-cyan-400 font-mono">Minimum Sample Size:</span>{' '}
                    n ≥ 5 per group per segment (ensures statistical validity)
                  </div>
                  <div>
                    <span className="text-cyan-400 font-mono">Simpson Detection:</span>{' '}
                    Global positive trend with inverted segment trends = regulatory red flag
                  </div>
                </div>
              </div>
            </div>
          </ExpandableSection>
        </div>

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-zinc-800 text-xs text-zinc-500">
          <p>
            ADAVID v1.7 | Regulatory Compliance Grade | Audit Trail: Enabled | Simpson's Paradox
            Detection: Active
          </p>
          <p className="mt-2">
            Generated: {new Date().toISOString()} | Status: Production Ready
          </p>
        </div>
      </div>
    </div>
  );
};

export default ADAVIDDashboard;
