/**
 * Landing/Home page component
 */

import React from 'react';
import {
  BarChart3,
  Target,
  Shield,
  TrendingUp,
  ArrowRight,
  Zap,
  Users,
  Brain,
  LineChart,
  PieChart,
  Activity,
} from 'lucide-react';

export function HomePage({ onNavigate }) {
  return (
    <div style={{ paddingTop: '60px' }}>
      {/* Hero Section */}
      <HeroSection onNavigate={onNavigate} />
      
      {/* Problem Section */}
      <ProblemSection />
      
      {/* Features Section */}
      <FeaturesSection />
      
      {/* How It Works */}
      <HowItWorksSection />
      
      {/* Methodology Section */}
      <MethodologySection />
      
      {/* CTA Section */}
      <CTASection onNavigate={onNavigate} />
      
      {/* Footer */}
      <Footer />
    </div>
  );
}

function HeroSection({ onNavigate }) {
  return (
    <section style={{
      minHeight: 'calc(100vh - 60px)',
      background: 'linear-gradient(135deg, var(--gray-900) 0%, #1a1a2e 50%, var(--gray-900) 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '60px 24px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background decoration */}
      <div style={{
        position: 'absolute',
        top: '20%',
        left: '10%',
        width: '300px',
        height: '300px',
        background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(60px)',
      }} />
      <div style={{
        position: 'absolute',
        bottom: '20%',
        right: '10%',
        width: '400px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(124, 58, 237, 0.1) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(80px)',
      }} />

      <div style={{
        textAlign: 'center',
        maxWidth: '800px',
        position: 'relative',
        zIndex: 1,
      }}>
        {/* Logo */}
        <div style={{
          width: '100px',
          height: '100px',
          borderRadius: '24px',
          background: 'linear-gradient(135deg, var(--primary-500), #7c3aed)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 32px',
          boxShadow: '0 20px 60px rgba(59, 130, 246, 0.4)',
        }}>
          <BarChart3 size={48} color="white" />
        </div>

        {/* Title */}
        <h1 style={{
          fontSize: 'clamp(36px, 6vw, 64px)',
          fontWeight: 800,
          color: 'white',
          marginBottom: '20px',
          lineHeight: 1.1,
        }}>
          Pijar PT Expansion
          <br />
          <span style={{
            background: 'linear-gradient(135deg, #60a5fa, #a78bfa)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Decision System
          </span>
        </h1>

        {/* Subtitle */}
        <p style={{
          fontSize: 'clamp(16px, 2.5vw, 22px)',
          color: 'var(--gray-400)',
          marginBottom: '40px',
          lineHeight: 1.6,
          maxWidth: '600px',
          margin: '0 auto 40px',
        }}>
          Quantitative decision support for strategic market expansion
          into Indonesian higher education. Replace gut feelings with
          probability-based insights.
        </p>

        {/* CTA Buttons */}
        <div style={{
          display: 'flex',
          gap: '16px',
          justifyContent: 'center',
          flexWrap: 'wrap',
        }}>
          <button
            onClick={() => onNavigate('dashboard')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '10px',
              padding: '18px 36px',
              fontSize: '16px',
              fontWeight: 600,
              backgroundColor: 'var(--primary-500)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: 'pointer',
              boxShadow: '0 8px 30px rgba(59, 130, 246, 0.4)',
              transition: 'all var(--transition-normal)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 12px 40px rgba(59, 130, 246, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 8px 30px rgba(59, 130, 246, 0.4)';
            }}
          >
            Launch Decision System
            <ArrowRight size={20} />
          </button>

          <button
            onClick={() => {
              document.getElementById('methodology')?.scrollIntoView({ behavior: 'smooth' });
            }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '10px',
              padding: '18px 36px',
              fontSize: '16px',
              fontWeight: 600,
              backgroundColor: 'transparent',
              color: 'var(--gray-300)',
              border: '1px solid var(--gray-700)',
              borderRadius: '12px',
              cursor: 'pointer',
              transition: 'all var(--transition-normal)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--gray-500)';
              e.currentTarget.style.color = 'white';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--gray-700)';
              e.currentTarget.style.color = 'var(--gray-300)';
            }}
          >
            Learn More
          </button>
        </div>

        {/* Stats */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '48px',
          marginTop: '60px',
          flexWrap: 'wrap',
        }}>
          {[
            { value: '500+', label: 'Simulations' },
            { value: '36', label: 'Month Horizon' },
            { value: '15+', label: 'Risk Metrics' },
          ].map((stat, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: '36px',
                fontWeight: 700,
                color: 'white',
              }}>
                {stat.value}
              </div>
              <div style={{
                fontSize: '14px',
                color: 'var(--gray-500)',
              }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ProblemSection() {
  return (
    <section style={{
      padding: '100px 24px',
      backgroundColor: 'white',
    }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: 700,
            color: 'var(--gray-900)',
            marginBottom: '16px',
          }}>
            The Problem with Traditional Planning
          </h2>
          <p style={{
            fontSize: '18px',
            color: 'var(--gray-600)',
            maxWidth: '600px',
            margin: '0 auto',
            lineHeight: 1.7,
          }}>
            Single-point forecasts hide risk. "We'll make 500M profit" doesn't tell you
            about the 30% chance of losing 200M.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px',
        }}>
          {[
            {
              icon: Target,
              title: 'Quantify Uncertainty',
              description: 'Express inputs as probability distributions, not single numbers. "4-9 months, most likely 6" is more honest than "6 months."',
            },
            {
              icon: Activity,
              title: 'Explore Trade-offs',
              description: 'See how changing assumptions affects outcomes in real-time. What if win rates drop 10%? What if development takes longer?',
            },
            {
              icon: Shield,
              title: 'Manage Downside',
              description: 'Understand tail risks before committing capital. Know your Value at Risk and what drives worst-case scenarios.',
            },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <div
                key={i}
                style={{
                  padding: '32px',
                  backgroundColor: 'var(--gray-50)',
                  borderRadius: '16px',
                  transition: 'transform var(--transition-normal)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '14px',
                  backgroundColor: 'var(--primary-100)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '20px',
                }}>
                  <Icon size={28} style={{ color: 'var(--primary-600)' }} />
                </div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: 600,
                  color: 'var(--gray-900)',
                  marginBottom: '12px',
                }}>
                  {item.title}
                </h3>
                <p style={{
                  fontSize: '15px',
                  color: 'var(--gray-600)',
                  lineHeight: 1.6,
                }}>
                  {item.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function FeaturesSection() {
  const features = [
    {
      icon: LineChart,
      title: 'Monte Carlo Simulation',
      description: '500+ scenario paths with percentile bands and fan visualization',
    },
    {
      icon: PieChart,
      title: 'Outcome Distribution',
      description: 'See probability of profit, doubling, loss, and ruin',
    },
    {
      icon: Shield,
      title: 'Risk Analytics',
      description: 'VaR, CVaR, drawdown analysis, and survival curves',
    },
    {
      icon: Brain,
      title: 'Data-Driven Premortem',
      description: 'Understand why failures happen before they do',
    },
    {
      icon: Zap,
      title: 'Sensitivity Analysis',
      description: 'Tornado diagrams show which parameters matter most',
    },
    {
      icon: Users,
      title: 'Regime Switching',
      description: 'Model normal, stressed, and boom economic conditions',
    },
  ];

  return (
    <section style={{
      padding: '100px 24px',
      backgroundColor: 'var(--gray-50)',
    }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: 700,
            color: 'var(--gray-900)',
            marginBottom: '16px',
          }}>
            Trading-Desk Rigor for Business Decisions
          </h2>
          <p style={{
            fontSize: '18px',
            color: 'var(--gray-600)',
            maxWidth: '600px',
            margin: '0 auto',
          }}>
            The same quantitative methods banks use to manage billions in risk,
            applied to your strategic expansion decision.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px',
        }}>
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <div
                key={i}
                style={{
                  padding: '24px',
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  border: '1px solid var(--gray-200)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '16px',
                }}
              >
                <div style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '10px',
                  backgroundColor: 'var(--primary-50)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <Icon size={22} style={{ color: 'var(--primary-600)' }} />
                </div>
                <div>
                  <h3 style={{
                    fontSize: '16px',
                    fontWeight: 600,
                    color: 'var(--gray-900)',
                    marginBottom: '6px',
                  }}>
                    {feature.title}
                  </h3>
                  <p style={{
                    fontSize: '14px',
                    color: 'var(--gray-600)',
                    lineHeight: 1.5,
                  }}>
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function HowItWorksSection() {
  const steps = [
    {
      number: '01',
      title: 'Input Assumptions',
      items: ['Capital & timeline', 'Sales & conversion rates', 'Pricing tiers', 'Risk events'],
    },
    {
      number: '02',
      title: 'Run Simulation',
      items: ['500+ Monte Carlo paths', 'Month-by-month evolution', 'Regime switching', 'Stochastic shocks'],
    },
    {
      number: '03',
      title: 'Analyze Results',
      items: ['Probability distributions', 'Risk metrics (VaR/CVaR)', 'Sensitivity analysis', 'Premortem insights'],
    },
  ];

  return (
    <section style={{
      padding: '100px 24px',
      backgroundColor: 'white',
    }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: 700,
            color: 'var(--gray-900)',
            marginBottom: '16px',
          }}>
            How It Works
          </h2>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '40px',
        }}>
          {steps.map((step, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                backgroundColor: 'var(--primary-500)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px',
                fontWeight: 700,
                margin: '0 auto 20px',
                boxShadow: '0 8px 24px rgba(59, 130, 246, 0.3)',
              }}>
                {step.number}
              </div>
              <h3 style={{
                fontSize: '20px',
                fontWeight: 600,
                color: 'var(--gray-900)',
                marginBottom: '16px',
              }}>
                {step.title}
              </h3>
              <ul style={{
                listStyle: 'none',
                padding: 0,
                margin: 0,
              }}>
                {step.items.map((item, j) => (
                  <li
                    key={j}
                    style={{
                      fontSize: '14px',
                      color: 'var(--gray-600)',
                      padding: '8px 0',
                      borderBottom: j < step.items.length - 1 ? '1px solid var(--gray-100)' : 'none',
                    }}
                  >
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function MethodologySection() {
  return (
    <section 
      id="methodology"
      style={{
        padding: '100px 24px',
        backgroundColor: 'var(--gray-900)',
        color: 'white',
      }}
    >
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: 700,
            marginBottom: '16px',
          }}>
            The Quant Methodology
          </h2>
          <p style={{
            fontSize: '18px',
            color: 'var(--gray-400)',
            maxWidth: '600px',
            margin: '0 auto',
          }}>
            Built on rigorous statistical foundations
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '24px',
        }}>
          {[
            {
              title: 'Input Distributions',
              items: [
                'Triangular: Bounded expert estimates',
                'Beta: Rates and proportions',
                'Log-Normal: Right-skewed values',
                'Gamma: Waiting times and durations',
              ],
            },
            {
              title: 'Stochastic Processes',
              items: [
                'Poisson: Discrete event arrivals',
                'GBM: Continuous proportional growth',
                'Jump-Diffusion: Sudden shocks',
                'Markov Regimes: Economic states',
              ],
            },
            {
              title: 'Risk Metrics',
              items: [
                'VaR: Maximum loss at confidence level',
                'CVaR: Expected loss in tail',
                'Drawdown: Peak-to-trough decline',
                'Survival: Time-dependent ruin probability',
              ],
            },
            {
              title: 'Premortem Analysis',
              items: [
                'Cause Attribution: Why failures happen',
                'Critical Periods: When risk peaks',
                'Trajectories: How failures unfold',
                'Early Warnings: What to watch',
              ],
            },
          ].map((section, i) => (
            <div
              key={i}
              style={{
                padding: '28px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '16px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
              }}
            >
              <h3 style={{
                fontSize: '18px',
                fontWeight: 600,
                marginBottom: '16px',
                color: 'var(--primary-300)',
              }}>
                {section.title}
              </h3>
              <ul style={{
                listStyle: 'none',
                padding: 0,
                margin: 0,
              }}>
                {section.items.map((item, j) => (
                  <li
                    key={j}
                    style={{
                      fontSize: '14px',
                      color: 'var(--gray-300)',
                      padding: '8px 0',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                    }}
                  >
                    <span style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--primary-400)',
                      flexShrink: 0,
                    }} />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTASection({ onNavigate }) {
  return (
    <section style={{
      padding: '80px 24px',
      background: 'linear-gradient(135deg, var(--primary-600), #7c3aed)',
      textAlign: 'center',
    }}>
      <h2 style={{
        fontSize: '32px',
        fontWeight: 700,
        color: 'white',
        marginBottom: '16px',
      }}>
        Ready to Make Data-Driven Decisions?
      </h2>
      <p style={{
        fontSize: '18px',
        color: 'rgba(255, 255, 255, 0.8)',
        marginBottom: '32px',
      }}>
        Explore scenarios, understand risks, and decide with confidence.
      </p>
      <button
        onClick={() => onNavigate('dashboard')}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '10px',
          padding: '18px 40px',
          fontSize: '16px',
          fontWeight: 600,
          backgroundColor: 'white',
          color: 'var(--primary-600)',
          border: 'none',
          borderRadius: '12px',
          cursor: 'pointer',
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
        }}
      >
        Open Decision System
        <ArrowRight size={20} />
      </button>
    </section>
  );
}

function Footer() {
  return (
    <footer style={{
      backgroundColor: 'var(--gray-900)',
      padding: '20px 24px',
      borderTop: '1px solid var(--gray-800)',
    }}>
      <div style={{
        maxWidth: '1000px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '20px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'var(--primary-500)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <BarChart3 size={18} color="white" />
          </div>
          <span style={{
            fontWeight: 600,
            color: 'white',
            fontSize: '15px',
          }}>
            Pijar DSS
          </span>
        </div>
        <div style={{
          fontSize: '13px',
          color: 'var(--gray-500)',
        }}>
          © 2026 Pijar by Telkom Indonesia • Internship Project • Quantitative Decision Support System v1.0
        </div>
      </div>
    </footer>
  );
}