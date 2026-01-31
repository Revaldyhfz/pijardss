/**
 * User Guide / Manual Page
 * Easy-to-understand explanations with analogies
 */

import React, { useState } from 'react';
import {
  BookOpen,
  BarChart3,
  Target,
  Shield,
  TrendingUp,
  AlertTriangle,
  Activity,
  HelpCircle,
  ChevronRight,
  Lightbulb,
  Zap,
  Clock,
  DollarSign,
  Users,
  Percent,
  PieChart,
  LineChart,
} from 'lucide-react';

const sections = [
  { id: 'overview', label: 'Overview', icon: BookOpen },
  { id: 'why', label: 'Why This Matters', icon: Lightbulb },
  { id: 'inputs', label: 'Input Parameters', icon: DollarSign },
  { id: 'simulation', label: 'How Simulation Works', icon: Activity },
  { id: 'charts', label: 'Understanding Charts', icon: LineChart },
  { id: 'metrics', label: 'Key Metrics', icon: Target },
  { id: 'risk', label: 'Risk Analysis', icon: Shield },
  { id: 'premortem', label: 'Premortem Analysis', icon: AlertTriangle },
  { id: 'decisions', label: 'Making Decisions', icon: TrendingUp },
];

export function GuidePage({ onNavigate }) {
  const [activeSection, setActiveSection] = useState('overview');

  return (
    <div style={{ paddingTop: '60px', minHeight: '100vh', backgroundColor: 'var(--gray-50)' }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '40px 24px',
        display: 'grid',
        gridTemplateColumns: '240px 1fr',
        gap: '40px',
      }}>
        {/* Sidebar */}
        <nav style={{ position: 'sticky', top: '100px', height: 'fit-content' }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--gray-200)',
            overflow: 'hidden',
          }}>
            <div style={{
              padding: '16px 20px',
              borderBottom: '1px solid var(--gray-100)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}>
              <BookOpen size={20} style={{ color: 'var(--primary-500)' }} />
              <span style={{ fontWeight: 600, color: 'var(--gray-800)' }}>User Guide</span>
            </div>
            <div style={{ padding: '8px' }}>
              {sections.map((section) => {
                const Icon = section.icon;
                const isActive = activeSection === section.id;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      border: 'none',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: isActive ? 'var(--primary-50)' : 'transparent',
                      color: isActive ? 'var(--primary-600)' : 'var(--gray-600)',
                      fontSize: '13px',
                      fontWeight: isActive ? 600 : 500,
                      cursor: 'pointer',
                      textAlign: 'left',
                    }}
                  >
                    <Icon size={16} />
                    {section.label}
                  </button>
                );
              })}
            </div>
          </div>
          <button
            onClick={() => onNavigate('dashboard')}
            style={{
              width: '100%',
              marginTop: '16px',
              padding: '14px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              border: 'none',
              borderRadius: 'var(--radius-lg)',
              backgroundColor: 'var(--primary-500)',
              color: 'white',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Open Decision System
            <ChevronRight size={18} />
          </button>
        </nav>

        {/* Content */}
        <main style={{
          backgroundColor: 'white',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--gray-200)',
          padding: '40px',
        }}>
          {renderSection(activeSection)}
        </main>
      </div>
    </div>
  );
}

function renderSection(id) {
  switch (id) {
    case 'overview': return <OverviewSection />;
    case 'why': return <WhySection />;
    case 'inputs': return <InputsSection />;
    case 'simulation': return <SimulationSection />;
    case 'charts': return <ChartsSection />;
    case 'metrics': return <MetricsSection />;
    case 'risk': return <RiskSection />;
    case 'premortem': return <PremortemGuideSection />;
    case 'decisions': return <DecisionsSection />;
    default: return <OverviewSection />;
  }
}

// Reusable Components
function SectionTitle({ children, icon: Icon }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
      {Icon && (
        <div style={{
          width: '40px', height: '40px', borderRadius: '10px',
          backgroundColor: 'var(--primary-100)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Icon size={22} style={{ color: 'var(--primary-600)' }} />
        </div>
      )}
      <h2 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--gray-900)', margin: 0 }}>{children}</h2>
    </div>
  );
}

function Analogy({ title, children }) {
  return (
    <div style={{
      backgroundColor: 'var(--primary-50)',
      border: '1px solid var(--primary-200)',
      borderRadius: 'var(--radius-lg)',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
        <Lightbulb size={18} style={{ color: 'var(--primary-600)' }} />
        <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-600)' }}>
          {title || 'Think of it like...'}
        </span>
      </div>
      <p style={{ fontSize: '14px', color: 'var(--gray-700)', margin: 0, lineHeight: 1.7 }}>{children}</p>
    </div>
  );
}

function Para({ children }) {
  return <p style={{ fontSize: '15px', color: 'var(--gray-700)', lineHeight: 1.8, marginBottom: '16px' }}>{children}</p>;
}

function SubSection({ title, children }) {
  return (
    <div style={{ marginBottom: '32px' }}>
      <h3 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--gray-800)', marginBottom: '12px' }}>{title}</h3>
      {children}
    </div>
  );
}

// Sections
function OverviewSection() {
  return (
    <div>
      <SectionTitle icon={BookOpen}>What is Pijar DSS?</SectionTitle>
      <Para>
        Pijar DSS (Decision Support System) helps you make better strategic decisions about Pijar's 
        expansion into Indonesian higher education. Instead of single-point forecasts, it uses 
        <strong> Monte Carlo simulation</strong> to explore thousands of possible futures.
      </Para>
      <Analogy>
        Planning a road trip? Instead of assuming "5 hours," you consider: traffic might be light (4 hours) 
        or heavy (7 hours). This tool does the same for business—it shows the RANGE of outcomes and their probabilities.
      </Analogy>
      <SubSection title="What You'll Get">
        <ul style={{ paddingLeft: '24px', lineHeight: 2, color: 'var(--gray-700)' }}>
          <li><strong>Probability estimates</strong> — "78% chance of profit" beats "we'll make money"</li>
          <li><strong>Risk metrics</strong> — Know your downside before committing capital</li>
          <li><strong>Sensitivity analysis</strong> — Which assumptions matter most</li>
          <li><strong>Premortem analysis</strong> — Why failures happen, before they do</li>
        </ul>
      </SubSection>
    </div>
  );
}

function WhySection() {
  return (
    <div>
      <SectionTitle icon={Lightbulb}>Why This Matters</SectionTitle>
      <SubSection title="The Problem with Traditional Planning">
        <Para>
          Traditional plans give one number: "We project $2M revenue." This hides crucial information. 
          That number could be wildly optimistic or conservative—you can't tell.
        </Para>
        <Analogy title="Weather Forecasting">
          "It will be 25°C" is less useful than "70% chance of 23-27°C, 20% chance of rain." 
          The second lets you plan for uncertainty. This tool gives you that "umbrella forecast" for business.
        </Analogy>
      </SubSection>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '20px' }}>
        <div style={{ padding: '20px', backgroundColor: 'var(--danger-50)', borderRadius: 'var(--radius-lg)', border: '1px solid #fecaca' }}>
          <div style={{ fontWeight: 600, color: 'var(--danger-600)', marginBottom: '8px' }}>❌ Single-Point Forecast</div>
          <div style={{ fontSize: '14px', color: 'var(--gray-600)' }}>
            "We'll make IDR 500M profit"<br/>Hides uncertainty.
          </div>
        </div>
        <div style={{ padding: '20px', backgroundColor: 'var(--success-50)', borderRadius: 'var(--radius-lg)', border: '1px solid #a7f3d0' }}>
          <div style={{ fontWeight: 600, color: 'var(--success-600)', marginBottom: '8px' }}>✓ Probabilistic Forecast</div>
          <div style={{ fontSize: '14px', color: 'var(--gray-600)' }}>
            "78% chance of profit, 3% ruin risk"<br/>Shows full picture.
          </div>
        </div>
      </div>
    </div>
  );
}

function InputsSection() {
  return (
    <div>
      <SectionTitle icon={DollarSign}>Understanding Input Parameters</SectionTitle>
      <Para>The sidebar contains assumptions you can adjust. Each affects simulation differently.</Para>
      <SubSection title="Capital & Development">
        <ParamCard name="Initial Capital" desc="Starting money (millions IDR)" example="5,000M = IDR 5B" tip="Higher = more runway for slow starts" />
        <ParamCard name="Dev Duration" desc="Months before you can sell" example="6 months → sales in month 7" tip="Longer dev = more burn before revenue" />
        <ParamCard name="Monthly Burn" desc="Monthly costs during development" example="200M/month" tip="Total dev cost = Duration × Burn" />
      </SubSection>
      <SubSection title="Sales & Conversion">
        <ParamCard name="Leads per Month" desc="Qualified prospects entering pipeline" example="7 leads = 7 PTs contacted monthly" tip="More leads = more opportunities" />
        <ParamCard name="BUMN Win Rate" desc="Closing probability for BUMN-affiliated PTs" example="70% = 7 of 10 deals close" tip="Telkom affiliation helps here" />
        <ParamCard name="Open Win Rate" desc="Closing probability in open market" example="22% = ~1 in 5 close" tip="Open market is competitive" />
      </SubSection>
    </div>
  );
}

function ParamCard({ name, desc, example, tip }) {
  return (
    <div style={{ padding: '14px', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)', border: '1px solid var(--gray-200)', marginBottom: '10px' }}>
      <div style={{ fontWeight: 600, color: 'var(--gray-800)', marginBottom: '4px' }}>{name}</div>
      <div style={{ fontSize: '13px', color: 'var(--gray-600)', marginBottom: '6px' }}>{desc}</div>
      <div style={{ fontSize: '12px', color: 'var(--primary-600)', backgroundColor: 'var(--primary-50)', padding: '4px 8px', borderRadius: 'var(--radius-sm)', display: 'inline-block', marginBottom: '6px' }}>Ex: {example}</div>
      <div style={{ fontSize: '11px', color: 'var(--gray-500)' }}>💡 {tip}</div>
    </div>
  );
}

function SimulationSection() {
  return (
    <div>
      <SectionTitle icon={Activity}>How the Simulation Works</SectionTitle>
      <SubSection title="The Process">
        <ol style={{ paddingLeft: '24px', lineHeight: 2.2, color: 'var(--gray-700)' }}>
          <li><strong>Set assumptions</strong> — Configure parameters in sidebar</li>
          <li><strong>Run simulation</strong> — System generates 500+ possible futures</li>
          <li><strong>Random variation</strong> — Each run varies inputs within realistic ranges</li>
          <li><strong>Month-by-month</strong> — Tracks capital, customers, revenue, costs</li>
          <li><strong>Record outcomes</strong> — Notes final capital, drawdowns, profit/loss</li>
          <li><strong>Aggregate</strong> — Combines all runs into probability distributions</li>
        </ol>
      </SubSection>
      <Analogy title="Dice Rolling">
        Rolling special dice 500 times. Each roll determines "how many leads" or "did deal close." 
        After 500 rolls, you see patterns: "got 6+ leads 70% of time." That's Monte Carlo—rolling 
        "business dice" many times to see outcome distributions.
      </Analogy>
    </div>
  );
}

function ChartsSection() {
  return (
    <div>
      <SectionTitle icon={LineChart}>Understanding the Charts</SectionTitle>
      <SubSection title="Equity Curve (Main Chart)">
        <Para>Shows capital over time across all simulations. Each line is one possible future.</Para>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '16px' }}>
          <LegendItem color="#10b981" label="Best" desc="Highest ending capital" />
          <LegendItem color="#3b82f6" label="Median" desc="50th percentile outcome" />
          <LegendItem color="#ef4444" label="Worst" desc="Lowest ending capital" />
        </div>
        <Analogy title="Stock Chart Analogy">
          Like stock charts, but instead of one historical line, you see many possible future lines. 
          The "fan" width shows uncertainty—narrow = predictable, wide = high variance.
        </Analogy>
      </SubSection>
      <SubSection title="Return Distribution">
        <Para>Shows how returns are distributed. X-axis is return %, height shows frequency.</Para>
        <ul style={{ paddingLeft: '24px', lineHeight: 2, color: 'var(--gray-700)', fontSize: '14px' }}>
          <li><span style={{ color: '#10b981', fontWeight: 600 }}>Green</span> = Profitable (return &gt; 0%)</li>
          <li><span style={{ color: '#ef4444', fontWeight: 600 }}>Red</span> = Loss (return &lt; 0%)</li>
        </ul>
      </SubSection>
      <SubSection title="Tornado Chart">
        <Para>Shows which parameters impact outcomes most. Top parameters matter most.</Para>
        <Analogy>
          Like testing recipe ingredients. Salt changes taste dramatically = "high sensitivity." 
          Parsley barely matters = "low sensitivity." Focus on high-sensitivity parameters.
        </Analogy>
      </SubSection>
    </div>
  );
}

function LegendItem({ color, label, desc }) {
  return (
    <div style={{ padding: '10px', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)', borderLeft: `3px solid ${color}` }}>
      <div style={{ fontWeight: 600, fontSize: '13px', color: 'var(--gray-800)' }}>{label}</div>
      <div style={{ fontSize: '11px', color: 'var(--gray-600)' }}>{desc}</div>
    </div>
  );
}

function MetricsSection() {
  return (
    <div>
      <SectionTitle icon={Target}>Key Metrics Explained</SectionTitle>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <MetricCard name="P(Profit)" meaning="Probability of ending with more than you started" good="≥70%" color="var(--success-600)" />
        <MetricCard name="P(2x)" meaning="Probability of doubling your investment" good="≥40%" color="var(--primary-600)" />
        <MetricCard name="P(Ruin)" meaning="Probability of complete capital depletion" good="≤5%" color="var(--danger-600)" />
        <MetricCard name="Mean Return" meaning="Average return across all simulations" good="Depends on risk tolerance" color="var(--warning-600)" />
        <MetricCard name="Max Drawdown" meaning="Largest peak-to-trough decline" good="≤40%" color="var(--gray-600)" />
      </div>
    </div>
  );
}

function MetricCard({ name, meaning, good, color }) {
  return (
    <div style={{ padding: '14px', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)', borderLeft: `4px solid ${color}` }}>
      <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--gray-800)', marginBottom: '4px' }}>{name}</div>
      <div style={{ fontSize: '14px', color: 'var(--gray-700)', marginBottom: '6px' }}>{meaning}</div>
      <div style={{ fontSize: '12px', color: 'var(--success-600)' }}>✓ Good: {good}</div>
    </div>
  );
}

function RiskSection() {
  return (
    <div>
      <SectionTitle icon={Shield}>Risk Analysis</SectionTitle>
      <SubSection title="Value at Risk (VaR)">
        <Para>Answers: "What's the maximum I could lose with X% confidence?" 95% VaR of 900M means: "95% confident I won't lose more than 900M."</Para>
        <Analogy>Weather saying "95% chance temp stays above 10°C." Still 5% chance it goes lower, but you can plan for the likely scenario.</Analogy>
      </SubSection>
      <SubSection title="Conditional VaR (CVaR)">
        <Para>Answers: "If things go badly (worst 5%), how bad on average?" More informative than VaR about tail risk.</Para>
        <Analogy>VaR says worst 5% days are below 10°C. CVaR says those days average 5°C. CVaR tells you HOW bad the bad days are.</Analogy>
      </SubSection>
      <SubSection title="Survival Curve">
        <Para>Shows probability of not going bankrupt over time. High curve = low ruin risk. Dropping curve = danger.</Para>
      </SubSection>
    </div>
  );
}

function PremortemGuideSection() {
  return (
    <div>
      <SectionTitle icon={AlertTriangle}>Premortem Analysis</SectionTitle>
      <Para>A premortem asks "if this fails, why will it have failed?" BEFORE starting, not after.</Para>
      <Analogy title="Medical Analogy">
        Doctors don't wait for heart attacks to study risk factors. They analyze thousands of patients 
        to identify warning signs. Our premortem analyzes thousands of simulated "failures" to identify causes.
      </Analogy>
      <SubSection title="Primary Failure Causes">
        <Para>Factors most strongly correlating with failure. High attribution (&gt;35%) = critical factor to focus on.</Para>
      </SubSection>
      <SubSection title="Failure Trajectories">
        <div style={{ display: 'grid', gap: '10px' }}>
          <TrajCard type="Slow Bleed" desc="Gradual decline as revenue never covers costs" />
          <TrajCard type="Sudden Collapse" desc="Quick failure after losing major customer" />
          <TrajCard type="Recovery Failure" desc="Initial success followed by decline from premature scaling" />
        </div>
      </SubSection>
    </div>
  );
}

function TrajCard({ type, desc }) {
  return (
    <div style={{ padding: '12px', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)', border: '1px solid var(--gray-200)' }}>
      <div style={{ fontWeight: 600, color: 'var(--gray-800)', marginBottom: '4px' }}>{type}</div>
      <div style={{ fontSize: '13px', color: 'var(--gray-600)' }}>{desc}</div>
    </div>
  );
}

function DecisionsSection() {
  return (
    <div>
      <SectionTitle icon={TrendingUp}>Making Decisions</SectionTitle>
      <SubSection title="Recommendations">
        <div style={{ display: 'grid', gap: '10px' }}>
          <RecCard level="PROCEED" color="#059669" criteria="P(Profit)≥80%, Mean≥50%, P(Ruin)<5%" />
          <RecCard level="CAUTION" color="#d97706" criteria="P(Profit)≥60%" />
          <RecCard level="REASSESS" color="#c2410c" criteria="P(Profit)≥40%" />
          <RecCard level="DO NOT PROCEED" color="#dc2626" criteria="P(Profit)<40%" />
        </div>
      </SubSection>
      <SubSection title="Important Caveats">
        <div style={{ backgroundColor: 'var(--warning-50)', border: '1px solid var(--warning-200)', borderRadius: 'var(--radius-lg)', padding: '20px' }}>
          <ul style={{ paddingLeft: '24px', lineHeight: 2, color: 'var(--gray-700)', fontSize: '14px', margin: 0 }}>
            <li>This is NOT a crystal ball—probabilities, not certainties</li>
            <li>Results depend on input quality—garbage in, garbage out</li>
            <li>Model can't capture everything (competitors, regulations)</li>
            <li>Use as ONE input to decisions, not the ONLY input</li>
          </ul>
        </div>
      </SubSection>
    </div>
  );
}

function RecCard({ level, color, criteria }) {
  return (
    <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', border: `2px solid ${color}30`, backgroundColor: `${color}08` }}>
      <span style={{ fontWeight: 700, fontSize: '14px', color, padding: '4px 12px', borderRadius: 'var(--radius-full)', backgroundColor: `${color}20`, marginRight: '12px' }}>{level}</span>
      <span style={{ fontSize: '13px', color: 'var(--gray-600)' }}>{criteria}</span>
    </div>
  );
}