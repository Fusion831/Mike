// Global Application State
let currentStep = 1;
let currentWorkspace = 'home';
let isAnalysisMode = false;
let policyId = null;
let policyName = '';
let isSnapshotOpen = false;
let currentAppState = 'home';

// Simulated Mock Data for offline testing
const mockPolicySummary = {
  policy_id: "demo-id",
  filename: "Blue_Cross_PPO_Policy.pdf",
  summary: {
    overview: {
      insurer_name: "Blue Cross Blue Shield",
      plan_name: "Preferred PPO Gold Plan",
      mikes_eli5_summary: "This plan is a Gold-tier PPO. It functions best for individuals seeking low deductibles and a broad provider network. The biggest financial risk is using an out-of-network provider, which incurs a separate, much higher deductible.",
      network_rules: "This is a PPO. You do not need a PCP referral to see specialists, and out-of-network care is covered but at a significantly higher cost share.",
      specialist_referral_required: false,
      referral_details: "No referral needed to see any specialist."
    },
    financials: {
      in_network_deductible: { amount: "$750", nuance: "Applies per individual, family max is $1,500" },
      out_of_network_deductible: { amount: "$2,500", nuance: "Applies separately from in-network cost shares" },
      out_of_pocket_max: { amount: "$4,500", nuance: "Does not apply to prescription drug copays" }
    },
    routine_care: {
      preventive_care: { cost: "$0 (Copay Waived)", conditions: "Must use an in-network provider" },
      primary_care: { cost: "$25 copay", conditions: "Deductible is waived for first 3 visits" },
      specialist: { cost: "$50 copay", conditions: "Prior authorization required for specialist physical therapy" }
    },
    emergency_care: {
      emergency_room: { cost: "$250 copay", conditions: "Copay waived if admitted to hospital" },
      ambulance: { cost: "20% coinsurance", conditions: "Applies after deductible is met" },
      urgent_care: { cost: "$45 copay", conditions: "Deductible waived" }
    },
    drug_tiers: [
      { tier_name: "Tier 1 Generic", cost: "$10 copay", notes: "No prior authorization needed" },
      { tier_name: "Tier 2 Preferred Brand", cost: "$35 copay", notes: "Quantity limit of 30-day supply applies" },
      { tier_name: "Tier 3 Non-Preferred Brand", cost: "$70 copay", notes: "Requires step therapy" },
      { tier_name: "Tier 4 Specialty", cost: "30% coinsurance", notes: "Requires prior authorization and specialty pharmacy" }
    ],
    prior_authorization_requirements: [
      { service: "MRI & CT Scans", details: "All high-tech imaging requires pre-certification from the insurer.", citation: "Section 4.2 - Diagnostic Services" },
      { service: "Outpatient Surgeries", details: "Must get approval at least 7 business days prior to scheduled surgery.", citation: "Section 9.1 - Surgical Pre-auth" }
    ],
    excluded_services: [
      { exclusion: "Cosmetic Procedures", explanation: "Unless required due to accidental injury occurring while covered.", citation: "Section 12.3 - General Exclusions" },
      { exclusion: "Adult Dental & Vision", explanation: "Separate standalone riders must be purchased.", citation: "Section 12.8 - Vision and Dental Limitations" }
    ],
    example_scenarios: [
      { scenario: "Broken Arm emergency care", estimated_user_cost: "$380", assumptions: ["In-network provider", "ER visit + X-ray"], explanation: "Pays $250 ER copay plus 20% coinsurance on X-ray imaging ($130) once deductible met." }
    ],
    denial_risks: [
      { risk: "Failing to get pre-auth for MRI", explanation: "Automatic 50% penalty on the total cost of the imaging procedure if not requested.", prevention_tip: "Ensure your diagnostic clinic faxes pre-auth details before scheduling.", citation: "Section 4 - Outpatient Facilities" },
      { risk: "Using out-of-network anesthesiologist", explanation: "Anesthesiologists at in-network hospitals are sometimes out-of-network, leading to balance billing.", prevention_tip: "Confirm with the surgical coordinator that all support clinicians are in-network.", citation: "Section 11 - Out-of-Network Penalties" }
    ]
  }
};

const mockCoverageResponse = {
  processing_status: "completed",
  answer: {
    decision: "conditionally_covered",
    short_answer: "Physical therapy is conditionally covered, but requires a pre-certification check and doctor referrals.",
    detailed_reasoning: "Your Gold PPO plan covers outpatient physical therapy up to 30 visits per calendar year. However, all physical therapy sessions following a surgical procedure require prior authorization from your primary care provider or orthopedist. Out-of-network services are subject to a 50% coinsurance share.",
    conditions: [
      "Must have a doctor's referral stating medical necessity",
      "Prior authorization must be secured before the 4th session",
      "Limit of 30 physical therapy visits per year"
    ],
    next_steps: [
      "Ask your orthopedist to send a referral order to the therapy facility",
      "Have the therapy center call BCBS to file a prior authorization request",
      "Confirm the physical therapist is an in-network provider"
    ],
    evidence: {
      summary: "Outpatient physical therapy benefits are outlined under outpatient rehabilitation services.",
      supporting_citations: [
        {
          citation_id: "cit_pt_1",
          document_id: "policy_doc_id",
          chunk_id: "chunk_pt_1",
          heading: "Section 6.4",
          subsection: "Rehabilitative Care Outpatient",
          page_number: 44,
          quoted_text: "Outpatient rehabilitative physical therapy services are covered up to a maximum of 30 visits per calendar year when determined medically necessary and pre-authorized after the 3rd visit.",
          citation_role: "supports_coverage"
        }
      ]
    },
    risks: [
      {
        category: "prior_auth_risk",
        severity: "high",
        statement: "Claims will be fully denied if prior authorization is not secured before the 4th visit.",
        mitigation_steps: ["Ask the therapy coordinator to verify pre-auth status before your second visit."],
        citations: []
      }
    ]
  },
  confidence: {
    level: "high",
    rationale: "Direct clauses in Section 6.4 clearly detail outpatient physical therapy limits and authorization conditions.",
    policy_grounding_status: "fully_grounded"
  },
  citations: [
    {
      citation_id: "cit_pt_1",
      document_id: "policy_doc_id",
      chunk_id: "chunk_pt_1",
      heading: "Section 6.4",
      subsection: "Rehabilitative Care Outpatient",
      page_number: 44,
      quoted_text: "Outpatient rehabilitative physical therapy services are covered up to a maximum of 30 visits per calendar year when determined medically necessary and pre-authorized after the 3rd visit.",
      citation_role: "supports_coverage"
    }
  ]
};

// Size overlays to window dimensions to prevent SVG coordinate scaling mismatch
function resizeOverlaySVGs() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const spotlight = document.getElementById('spotlight-overlay');
  const annotation = document.getElementById('annotation-layer');
  if (spotlight) {
    spotlight.setAttribute('width', w);
    spotlight.setAttribute('height', h);
  }
  if (annotation) {
    annotation.setAttribute('width', w);
    annotation.setAttribute('height', h);
  }
}

// Initial Setup
window.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  checkOnboardingStatus();
  adjustInputDock();
  resizeOverlaySVGs();
  window.addEventListener('resize', () => {
    adjustInputDock();
    resizeOverlaySVGs();
    if (document.getElementById('spotlight-overlay').classList.contains('hidden') === false) {
      updateSpotlight();
    }
  });
});

// Dynamic mount switcher for interactive area to avoid layout overlap
function adjustInputDock() {
  const interactiveArea = document.getElementById('chat-interactive-area');
  if (isAnalysisMode) {
    const chatDock = document.getElementById('chat-input-dock');
    if (chatDock && interactiveArea) {
      chatDock.appendChild(interactiveArea);
    }
  } else {
    const landingDock = document.getElementById('landing-input-dock');
    if (landingDock && interactiveArea) {
      landingDock.appendChild(interactiveArea);
    }
  }
}

// Onboarding Logic
let spotlightTargetId = '';
let spotlightPaddingX = 12;
let spotlightPaddingY = 12;
let spotlightRadius = 16;
let spotlightTrackingInterval = null;
let isStep1AnnotationInitialized = false;

function checkOnboardingStatus() {
  const completed = localStorage.getItem('mike_onboarding_completed');
  if (completed === 'true') {
    skipOnboarding();
  } else {
    startOnboarding();
  }
}

function startOnboarding() {
  currentStep = 1;
  isAnalysisMode = false;
  setWorkspace('home');
  adjustInputDock();
  
  // Ensure overlays are resized correctly relative to the current viewport
  resizeOverlaySVGs();
  
  // Add body class for backdrop blur / dim selectors
  document.body.classList.add('onboarding-active');
  
  document.getElementById('spotlight-overlay').classList.remove('hidden');
  
  // Blur and dim background components
  const blurOverlay = document.getElementById('onboarding-backdrop-blur');
  if (blurOverlay) {
    blurOverlay.classList.remove('hidden');
    setTimeout(() => {
      blurOverlay.classList.remove('opacity-0');
      blurOverlay.classList.add('opacity-100');
    }, 50);
  }
  
  // Show onboarding controls and instruction panels
  const instContainer = document.getElementById('onboarding-instruction-container');
  if (instContainer) {
    instContainer.classList.remove('hidden');
    setTimeout(() => {
      instContainer.classList.remove('opacity-0');
      instContainer.classList.add('opacity-100');
    }, 50);
  }
  
  const tourCard = document.getElementById('onboarding-tour-card');
  if (tourCard) {
    tourCard.classList.remove('hidden');
    setTimeout(() => {
      tourCard.classList.remove('opacity-0');
      tourCard.classList.add('opacity-100');
    }, 50);
  }
  
  document.getElementById('onboarding-cards').classList.add('hidden');
  
  updateOnboardingStep();
}

function updateOnboardingStep() {
  updateSpotlight();
  updateOnboardingControlsAndTracker();
}

// Update the dark SVG overlay spotlight mask coordinates
function updateSpotlight() {
  // Clean up previous annotations
  document.getElementById('annotation-layer').classList.add('hidden');
  isStep1AnnotationInitialized = false;
  isTabArrowInitialized = false;
  
  // Show onboarding cards only on Step 2, hide on other steps to prevent bleed-through
  const onboardingCards = document.getElementById('onboarding-cards');
  if (onboardingCards) {
    if (currentStep === 2) {
      onboardingCards.classList.remove('hidden');
      setTimeout(() => {
        onboardingCards.style.opacity = '1';
        onboardingCards.style.transform = 'scale(1)';
        const cards = onboardingCards.querySelectorAll('button');
        if (cards && cards.length > 0) {
          cards[0].focus();
        }
      }, 50);
    } else {
      onboardingCards.classList.add('hidden');
      onboardingCards.style.opacity = '0';
      onboardingCards.style.transform = 'scale(0.95)';
    }
  }
  
  // Dynamic z-indexing for parent container to keep inputs/cards sharp above backdrop filter
  const interactiveArea = document.getElementById('chat-interactive-area');
  if (currentStep === 1 || currentStep === 2) {
    interactiveArea.classList.add('relative', 'z-50');
  } else {
    interactiveArea.classList.remove('relative', 'z-50');
  }
  
  if (currentStep === 1) {
    spotlightTargetId = 'upload-btn';
    spotlightPaddingX = 8;
    spotlightPaddingY = 8;
    spotlightRadius = 12;
  } else if (currentStep === 2) {
    spotlightTargetId = 'onboarding-cards';
    spotlightPaddingX = 12;
    spotlightPaddingY = 12;
    spotlightRadius = 16;
  } else if (currentStep === 3) {
    spotlightTargetId = 'nav-segmented-control';
    spotlightPaddingX = 16;
    spotlightPaddingY = 10;
    spotlightRadius = 9999;
    setWorkspace('home');
  } else if (currentStep === 4) {
    spotlightTargetId = 'nav-segmented-control';
    spotlightPaddingX = 16;
    spotlightPaddingY = 10;
    spotlightRadius = 9999;
    setWorkspace('defense');
  }

  // Bring target above the mask overlay so it is clickable
  highlightElement(spotlightTargetId);

  // Start continuous tracking loop for 1.2s to align with layout transitions
  startSpotlightTracking(1200);
}

function startSpotlightTracking(duration = 1200) {
  if (spotlightTrackingInterval) {
    clearInterval(spotlightTrackingInterval);
  }
  const startTime = Date.now();
  
  // Update coordinates immediately
  updateSpotlightCoords();
  
  spotlightTrackingInterval = setInterval(() => {
    updateSpotlightCoords();
    if (Date.now() - startTime >= duration) {
      clearInterval(spotlightTrackingInterval);
      spotlightTrackingInterval = null;
    }
  }, 16); // ~60fps
}

function updateSpotlightCoords() {
  const hole = document.getElementById('spotlight-hole');
  const target = document.getElementById(spotlightTargetId);
  
  if (target && hole) {
    const rect = target.getBoundingClientRect();
    hole.setAttribute('x', rect.left - spotlightPaddingX);
    hole.setAttribute('y', rect.top - spotlightPaddingY);
    hole.setAttribute('width', rect.width + (spotlightPaddingX * 2));
    hole.setAttribute('height', rect.height + (spotlightPaddingY * 2));
    hole.setAttribute('rx', spotlightRadius);
    hole.setAttribute('ry', spotlightRadius);
    
    // Custom SVG sketch annotations for Step 1, 3, and 4
    if (currentStep === 1) {
      drawHanddrawnCircleAndArrow(rect);
    } else if (currentStep === 3) {
      drawOnboardingTabArrow('tab-home');
    } else if (currentStep === 4) {
      drawOnboardingTabArrow('tab-defense');
    }
  }
}

// Calculate dynamic, mathematically correct arrowhead paths aligned to the curve's end tangent
function calculateArrowHead(cp2X, cp2Y, endX, endY, length = 12, angleDeg = 30) {
  const dx = endX - cp2X;
  const dy = endY - cp2Y;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len === 0) return '';
  
  const udx = dx / len;
  const udy = dy / len;
  
  const angleRad = (angleDeg * Math.PI) / 180;
  const backX = -udx;
  const backY = -udy;
  
  const leftX = endX + length * (backX * Math.cos(angleRad) - backY * Math.sin(angleRad));
  const leftY = endY + length * (backX * Math.sin(angleRad) + backY * Math.cos(angleRad));
  
  const rightX = endX + length * (backX * Math.cos(-angleRad) - backY * Math.sin(-angleRad));
  const rightY = endY + length * (backX * Math.sin(-angleRad) + backY * Math.cos(-angleRad));
  
  return `M ${leftX} ${leftY} L ${endX} ${endY} L ${rightX} ${rightY}`;
}

// Mathematical calculation for the sketchy circle and arrow points
function drawHanddrawnCircleAndArrow(btnRect) {
  const layer = document.getElementById('annotation-layer');
  layer.classList.remove('hidden');
  
  const circle = document.getElementById('annotation-circle');
  const arrow = document.getElementById('annotation-arrow');
  const arrowHead = document.getElementById('annotation-arrow-head');
  
  // Geometric circle coordinates centered around the "+" button
  const cx = btnRect.left + (btnRect.width / 2);
  const cy = btnRect.top + (btnRect.height / 2);
  const r = (btnRect.width / 2) + 6;
  
  // Clean geometric circle SVG path
  const dCircle = `M ${cx} ${cy - r} A ${r} ${r} 0 1 1 ${cx - 0.01} ${cy - r} Z`;
  circle.setAttribute('d', dCircle);
  
  // Get instruction callout bottom center coordinates to start the arrow
  const instruction = document.getElementById('onboarding-instruction-container');
  const instRect = instruction.getBoundingClientRect();
  const startX = instRect.left + (instRect.width / 2);
  const startY = instRect.bottom + 4;
  
  // Point to the top edge of the circle around the upload button
  const endX = cx;
  const endY = cy - r - 4;
  
  // Draw a curved bezier path sweeping down to the upload button
  const cp1X = startX - (startX - endX) * 0.25;
  const cp1Y = startY + (endY - startY) * 0.4;
  const cp2X = endX - (startX - endX) * 0.1;
  const cp2Y = endY - 50;
  
  const dArrow = `M ${startX} ${startY} C ${cp1X} ${cp1Y}, ${cp2X} ${cp2Y}, ${endX} ${endY}`;
  arrow.setAttribute('d', dArrow);
  
  // Arrow head paths pointing down towards target
  const dArrowHead = `M ${endX - 7} ${endY - 7} L ${endX} ${endY} L ${endX + 7} ${endY - 7}`;
  arrowHead.setAttribute('d', dArrowHead);
  
  if (!isStep1AnnotationInitialized) {
    isStep1AnnotationInitialized = true;
    
    // Reset styles and animate drawing effect once
    circle.style.transition = 'none';
    arrow.style.transition = 'none';
    circle.style.strokeDashoffset = '1000';
    arrow.style.strokeDashoffset = '1000';
    
    arrowHead.style.transition = 'none';
    arrowHead.style.opacity = '0';
    
    setTimeout(() => {
      circle.style.transition = 'stroke-dashoffset 800ms ease-in-out';
      arrow.style.transition = 'stroke-dashoffset 600ms ease-in-out';
      circle.style.strokeDashoffset = '0';
      arrow.style.strokeDashoffset = '0';
      
      // Animate arrowhead fade-in once the arrow line reaches the target
      setTimeout(() => {
        arrowHead.style.transition = 'opacity 250ms ease-in-out';
        arrowHead.style.opacity = '1';
      }, 500);
    }, 50);
  } else {
    arrowHead.style.transition = 'none';
    arrowHead.style.opacity = '1';
  }
}

let isTabArrowInitialized = false;

function drawOnboardingTabArrow(targetId) {
  const layer = document.getElementById('annotation-layer');
  layer.classList.remove('hidden');
  
  const circle = document.getElementById('annotation-circle');
  const arrow = document.getElementById('annotation-arrow');
  const arrowHead = document.getElementById('annotation-arrow-head');
  
  circle.setAttribute('d', '');
  
  const inst = document.getElementById('onboarding-instruction-container');
  const target = document.getElementById(targetId);
  
  if (inst && target && arrow && arrowHead) {
    const instRect = inst.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    
    let startX, startY, endX, endY, cp1X, cp1Y, cp2X, cp2Y;
    
    if (targetId === 'tab-home') {
      // Start at left center of instruction box
      startX = instRect.left - 4;
      startY = instRect.top + (instRect.height / 2);
      
      // End at bottom center of tab button
      endX = targetRect.left + (targetRect.width / 2);
      endY = targetRect.bottom + 8;
      
      // Bending curve sweeping out left, then up and right
      cp1X = startX - 120;
      cp1Y = startY + 20;
      cp2X = startX - 60;
      cp2Y = endY + 80;
      
      const dArrow = `M ${startX} ${startY} C ${cp1X} ${cp1Y}, ${cp2X} ${cp2Y}, ${endX} ${endY}`;
      arrow.setAttribute('d', dArrow);
      
      const dArrowHead = calculateArrowHead(cp2X, cp2Y, endX, endY, 12, 30);
      arrowHead.setAttribute('d', dArrowHead);
    } else {
      // Start at right center of instruction box (for Claim Defense tab)
      startX = instRect.right + 4;
      startY = instRect.top + (instRect.height / 2);
      
      // End at bottom center of tab button
      endX = targetRect.left + (targetRect.width / 2);
      endY = targetRect.bottom + 8;
      
      // Bending curve sweeping out right, then up and left
      cp1X = startX + 120;
      cp1Y = startY + 20;
      cp2X = startX + 60;
      cp2Y = endY + 80;
      
      const dArrow = `M ${startX} ${startY} C ${cp1X} ${cp1Y}, ${cp2X} ${cp2Y}, ${endX} ${endY}`;
      arrow.setAttribute('d', dArrow);
      
      // Arrow head pointing to the Claim Defense tab (approaching from bottom-right)
      const dArrowHead = calculateArrowHead(cp2X, cp2Y, endX, endY, 12, 30);
      arrowHead.setAttribute('d', dArrowHead);
    }
    
    if (!isTabArrowInitialized) {
      isTabArrowInitialized = true;
      arrow.style.transition = 'none';
      arrow.style.strokeDashoffset = '1000';
      
      arrowHead.style.transition = 'none';
      arrowHead.style.opacity = '0';
      
      setTimeout(() => {
        arrow.style.transition = 'stroke-dashoffset 800ms ease-in-out';
        arrow.style.strokeDashoffset = '0';
        
        // Fade in arrowhead after the 800ms drawing completes
        setTimeout(() => {
          arrowHead.style.transition = 'opacity 250ms ease-in-out';
          arrowHead.style.opacity = '1';
        }, 700);
      }, 50);
    } else {
      arrowHead.style.transition = 'none';
      arrowHead.style.opacity = '1';
    }
  }
}

let lastHighlightedElement = null;
let addedRelativeClass = false;

function highlightElement(elId) {
  if (lastHighlightedElement) {
    if (addedRelativeClass) {
      lastHighlightedElement.classList.remove('relative');
    }
    lastHighlightedElement.classList.remove('z-50');
    addedRelativeClass = false;
  }
  const el = document.getElementById(elId);
  if (el) {
    const hasPosition = el.classList.contains('relative') || 
                        el.classList.contains('absolute') || 
                        el.classList.contains('fixed');
    if (!hasPosition) {
      el.classList.add('relative');
      addedRelativeClass = true;
    }
    el.classList.add('z-50');
    lastHighlightedElement = el;
  } else {
    lastHighlightedElement = null;
    addedRelativeClass = false;
  }
}

function updateOnboardingControlsAndTracker() {
  const instruction = document.getElementById('onboarding-instruction-text');
  const btnPrev = document.getElementById('onboarding-prev-btn');
  const btnNext = document.getElementById('onboarding-next-btn');
  const skipBtn = document.getElementById('onboarding-skip-btn');
  
  // Dynamically position the instruction container: top-16 for slides 1/2, center-aligned for slides 3/4
  const instContainer = document.getElementById('onboarding-instruction-container');
  if (instContainer) {
    if (currentStep === 1 || currentStep === 2) {
      instContainer.style.top = '4rem'; // top-16
      instContainer.style.transform = 'translateX(-50%) translateY(0)';
    } else {
      instContainer.style.top = '40%'; // vertical center-ish
      instContainer.style.transform = 'translateX(-50%) translateY(-50%)';
    }
  }

  // 1. Update Instructions
  if (currentStep === 1) {
    instruction.innerText = "Attach your policy to get started";
    btnPrev.classList.add('opacity-50', 'pointer-events-none');
    btnNext.innerText = "Next";
    skipBtn.classList.remove('hidden');
  } else if (currentStep === 2) {
    instruction.innerText = "Ask Mike Anything";
    btnPrev.classList.remove('opacity-50', 'pointer-events-none');
    btnNext.innerText = "Next";
    skipBtn.classList.remove('hidden');
  } else if (currentStep === 3) {
    instruction.innerText = "Use Home to explore coverage, exclusions, benefits, waiting periods, and policy details.";
    btnPrev.classList.remove('opacity-50', 'pointer-events-none');
    btnNext.innerText = "Next";
    skipBtn.classList.remove('hidden');
  } else if (currentStep === 4) {
    instruction.innerText = "Use Claim Defense to understand claim denials, identify supporting evidence, and prepare stronger appeal responses.";
    btnPrev.classList.remove('opacity-50', 'pointer-events-none');
    btnNext.innerText = "Finish";
    skipBtn.classList.add('hidden');
  }
  
  // 2. Highlight active step capsule/tablet
  for (let i = 1; i <= 4; i++) {
    const lbl = document.getElementById(`step-lbl-${i}`);
    if (lbl) {
      if (i === currentStep) {
        lbl.className = "h-1.5 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg shadow-purple-500/30 transition-all duration-300";
      } else {
        lbl.className = "h-1.5 w-8 rounded-full bg-slate-800 transition-all duration-300";
      }
    }
  }
}

function onboardingNext() {
  if (currentStep < 4) {
    currentStep++;
    updateOnboardingStep();
  } else {
    finishOnboarding();
  }
}

function onboardingBack() {
  if (currentStep > 1) {
    currentStep--;
    updateOnboardingStep();
  }
}

function skipOnboarding(shouldTransition = true) {
  localStorage.setItem('mike_onboarding_completed', 'true');
  document.getElementById('spotlight-overlay').classList.add('hidden');
  document.getElementById('annotation-layer').classList.add('hidden');
  document.getElementById('onboarding-cards').classList.add('hidden');
  
  // Remove body active class
  document.body.classList.remove('onboarding-active');
  
  // Remove z-50 from interactive area
  const interactiveArea = document.getElementById('chat-interactive-area');
  if (interactiveArea) {
    interactiveArea.classList.remove('relative', 'z-50');
  }
  
  // Remove backdrop blur overlay
  const blurOverlay = document.getElementById('onboarding-backdrop-blur');
  if (blurOverlay) {
    blurOverlay.classList.remove('opacity-100');
    blurOverlay.classList.add('opacity-0');
    setTimeout(() => {
      blurOverlay.classList.add('hidden');
    }, 500);
  }
  
  // Hide onboarding panels
  const instContainer = document.getElementById('onboarding-instruction-container');
  if (instContainer) {
    instContainer.classList.remove('opacity-100');
    instContainer.classList.add('opacity-0');
    setTimeout(() => {
      instContainer.classList.add('hidden');
    }, 500);
  }
  
  const tourCard = document.getElementById('onboarding-tour-card');
  if (tourCard) {
    tourCard.classList.remove('opacity-100');
    tourCard.classList.add('opacity-0');
    setTimeout(() => {
      tourCard.classList.add('hidden');
    }, 500);
  }
  
  highlightElement(null);
  
  if (shouldTransition) {
    // Set default state
    setWorkspace('home');
    adjustInputDock();
    updateNavigationState();
  }
}

function finishOnboarding() {
  localStorage.setItem('mike_onboarding_completed', 'true');
  skipOnboarding();
  
  // Show subtle completion banner
  showSystemToast("You're all set. Upload a policy and start asking questions.");
}

// Workspace Swapper
function setWorkspace(type) {
  if (type === 'home') {
    transitionToState('home');
  } else if (type === 'conversation') {
    if (policyId) {
      transitionToState('conversation');
    }
  } else {
    transitionToState('defense');
  }
}

function updateNavigationState() {
  const tabChat = document.getElementById('tab-conversation');
  if (tabChat) {
    if (policyId) {
      tabChat.removeAttribute('disabled');
      tabChat.className = "relative z-10 flex-1 py-1.5 text-center text-sm font-medium text-slate-500 cursor-pointer transition-colors focus:outline-none";
    } else {
      tabChat.setAttribute('disabled', 'true');
      tabChat.className = "relative z-10 flex-1 py-1.5 text-center text-sm font-medium text-slate-500 opacity-40 cursor-not-allowed transition-colors focus:outline-none";
    }
  }
}

function transitionToState(newState) {
  const prevState = currentAppState;
  currentAppState = newState;
  
  console.log(`Transitioning state: ${prevState} -> ${newState}`);
  
  const navIndicator = document.getElementById('segmented-indicator');
  const btnHome = document.getElementById('tab-home');
  const btnConversation = document.getElementById('tab-conversation');
  const btnDefense = document.getElementById('tab-defense');
  
  const viewHome = document.getElementById('view-home');
  const viewConversation = document.getElementById('view-conversation');
  const viewDefense = document.getElementById('view-defense');
  
  const landingContainer = document.getElementById('landing-container');
  const chatArea = document.getElementById('chat-area');
  const policyCard = document.getElementById('policy-card-container');
  const starterChips = document.getElementById('starter-prompt-chips');
  
  // Helper to assign tab styles based on active status
  function updateTabStyle(btn, isActive, isEnabled = true) {
    if (!btn) return;
    if (isActive) {
      btn.className = "relative z-10 flex-1 py-1.5 text-center text-sm font-bold text-slate-800 transition-colors focus:outline-none";
    } else {
      if (isEnabled) {
        btn.className = "relative z-10 flex-1 py-1.5 text-center text-sm font-medium text-slate-500 transition-colors focus:outline-none";
      } else {
        btn.className = "relative z-10 flex-1 py-1.5 text-center text-sm font-medium text-slate-500 opacity-40 cursor-not-allowed transition-colors focus:outline-none";
      }
    }
  }

  // Tabs highlight updating
  if (newState === 'home') {
    if (navIndicator) navIndicator.style.transform = 'translateX(0)';
    updateTabStyle(btnHome, true);
    updateTabStyle(btnConversation, false, !!policyId);
    updateTabStyle(btnDefense, false);
  } else if (newState === 'conversation') {
    if (navIndicator) navIndicator.style.transform = 'translateX(100%)';
    updateTabStyle(btnHome, false);
    updateTabStyle(btnConversation, true, !!policyId);
    updateTabStyle(btnDefense, false);
  } else if (newState === 'defense') {
    if (navIndicator) navIndicator.style.transform = 'translateX(200%)';
    updateTabStyle(btnHome, false);
    updateTabStyle(btnConversation, false, !!policyId);
    updateTabStyle(btnDefense, true);
  }
  
  // Local fade out helper using css transitions
  function fadeOut(el, duration = 200) {
    if (!el || el.classList.contains('hidden')) return Promise.resolve();
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    return new Promise(resolve => {
      setTimeout(() => {
        el.classList.add('hidden');
        resolve();
      }, duration);
    });
  }
  
  // Local fade in helper
  function fadeIn(el) {
    if (!el) return;
    el.classList.remove('hidden');
    void el.offsetWidth;
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
    setTimeout(() => {
      if (el.style.opacity === '1') {
        el.style.opacity = '';
      }
      if (el.style.transform === 'translateY(0px)' || el.style.transform === 'translateY(0)') {
        el.style.transform = '';
      }
    }, 950);
  }
  
  if (newState === 'defense') {
    const hidePromises = [];
    if (viewHome && !viewHome.classList.contains('hidden')) {
      hidePromises.push(fadeOut(viewHome, 200));
    }
    if (viewConversation && !viewConversation.classList.contains('hidden')) {
      hidePromises.push(fadeOut(viewConversation, 200));
    }
    Promise.all(hidePromises).then(() => {
      fadeIn(viewDefense);
    });
  } else if (newState === 'home') {
    const hidePromises = [];
    if (viewDefense && !viewDefense.classList.contains('hidden')) {
      hidePromises.push(fadeOut(viewDefense, 200));
    }
    if (viewConversation && !viewConversation.classList.contains('hidden')) {
      hidePromises.push(fadeOut(viewConversation, 200));
    }
    
    Promise.all(hidePromises).then(() => {
      if (viewHome && viewHome.classList.contains('hidden')) {
        viewHome.classList.remove('hidden');
        void viewHome.offsetWidth;
      }
      fadeIn(viewHome);
      
      isAnalysisMode = false;
      adjustInputDock();
      toggleSnapshot(false);
      
      if (policyId) {
        if (policyCard) {
          policyCard.classList.remove('pointer-events-none');
          policyCard.style.opacity = '1';
          policyCard.style.transform = 'translateY(0)';
        }
        if (starterChips) {
          starterChips.classList.remove('hidden', 'pointer-events-none');
          void starterChips.offsetWidth;
          starterChips.style.opacity = '1';
          starterChips.style.transform = 'scale(1)';
        }
      } else {
        if (policyCard) {
          policyCard.style.opacity = '0';
          policyCard.style.transform = 'translateY(-16px)';
          policyCard.classList.add('pointer-events-none');
        }
        if (starterChips) {
          starterChips.style.opacity = '0';
          starterChips.style.transform = 'scale(0.95)';
          starterChips.classList.add('pointer-events-none');
        }
      }
      
      fadeIn(landingContainer);
    });
  } else if (newState === 'conversation') {
    const hidePromises = [];
    if (viewDefense && !viewDefense.classList.contains('hidden')) {
      hidePromises.push(fadeOut(viewDefense, 200));
    }
    if (viewHome && !viewHome.classList.contains('hidden')) {
      hidePromises.push(fadeOut(viewHome, 200));
    }
    
    Promise.all(hidePromises).then(() => {
      if (viewConversation && viewConversation.classList.contains('hidden')) {
        viewConversation.classList.remove('hidden');
        void viewConversation.offsetWidth;
      }
      fadeIn(viewConversation);
      
      isAnalysisMode = true;
      adjustInputDock();
      
      if (starterChips) {
        starterChips.classList.add('hidden', 'pointer-events-none');
        starterChips.style.opacity = '0';
      }
      
      toggleSnapshot(true);
      
      const convPolicyCard = document.getElementById('conversation-policy-card-container');
      if (convPolicyCard) {
        convPolicyCard.classList.remove('pointer-events-none');
        convPolicyCard.style.opacity = '1';
        convPolicyCard.style.transform = 'translateY(0)';
      }
      
      fadeIn(chatArea);
      scrollChatToBottom();
    });
  }
}

// Upload Policy Flow
function triggerFileUpload() {
  document.getElementById('file-uploader').click();
}

function handleFileSelected(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    alert("Only PDF policies are supported");
    return;
  }
  
  uploadPolicy(file);
}

function uploadPolicy(file) {
  policyName = file.name;
  policyId = uuidv4();
  
  const progressDiv = document.getElementById('upload-status');
  const progressBar = document.getElementById('upload-progress-bar');
  const progressText = document.getElementById('upload-progress-text');
  
  progressDiv.classList.remove('hidden');
  progressBar.style.width = '0%';
  progressText.innerText = '0%';
  
  const formData = new FormData();
  formData.append('file', file);
  
  // Increment progress bar to simulate upload phase
  let currentProgress = 0;
  const interval = setInterval(() => {
    if (currentProgress < 90) {
      currentProgress += 5;
      progressBar.style.width = `${currentProgress}%`;
      progressText.innerText = `${currentProgress}%`;
    }
  }, 150);

  const url = `/v1/policies/${policyId}/ingest`;
  fetch(url, {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Ingestion failed with status ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    // Once ingested successfully, fetch summary
    return fetch(`/v1/policies/${policyId}/summary`);
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Summary fetch failed with status ${response.status}`);
    }
    return response.json();
  })
  .then(summaryResponse => {
    clearInterval(interval);
    progressBar.style.width = '100%';
    progressText.innerText = '100%';
    setTimeout(() => {
      progressDiv.classList.add('hidden');
      transitionToAnalysisMode(summaryResponse.summary);
    }, 300);
  })
  .catch(err => {
    console.warn("Backend API ingestion failed, falling back to offline mock mode:", err);
    showSystemToast("Backend offline or missing API key. Loading demo fallback policy.");
    
    clearInterval(interval);
    progressBar.style.width = '100%';
    progressText.innerText = '100%';
    setTimeout(() => {
      progressDiv.classList.add('hidden');
      transitionToAnalysisMode(mockPolicySummary.summary);
    }, 300);
  });
}

// Transition from Onboarding to Analysis mode layout
function transitionToAnalysisMode(summary = null, autoTransitionState = 'home') {
  const activeSummary = summary || mockPolicySummary.summary;
  
  const bg = document.getElementById('app-bg');
  if (bg) bg.classList.add('analysis-mode');
  
  const cardName = document.getElementById('policy-card-name');
  if (cardName) cardName.innerText = policyName;
  const convCardName = document.getElementById('conversation-policy-card-name');
  if (convCardName) convCardName.innerText = policyName;
  
  populatePolicySnapshot(activeSummary);
  updateNavigationState();
  
  if (autoTransitionState) {
    transitionToState(autoTransitionState);
  }
}

function populatePolicySnapshot(summary) {
  const container = document.getElementById('snapshot-content-scroll');
  const overview = summary?.overview || {};
  const financials = summary?.financials || {};
  const routineCare = summary?.routine_care || {};
  const priorAuth = summary?.prior_authorization_requirements || [];
  const exclusions = summary?.excluded_services || [];

  container.innerHTML = `
    <!-- ELI5 Summary -->
    <div class="bg-slate-900/40 p-4 rounded-2xl border border-slate-800/80">
      <h4 class="text-xs font-bold text-slate-500 tracking-wider uppercase mb-1.5">Overview</h4>
      <p class="text-sm font-semibold text-slate-200 leading-normal">${overview.plan_name || 'N/A'}</p>
      <p class="text-xs text-slate-400 mt-2 leading-relaxed font-medium">${overview.mikes_eli5_summary || 'N/A'}</p>
    </div>

    <!-- Financials -->
    <div class="space-y-3">
      <h4 class="text-xs font-bold text-slate-500 tracking-wider uppercase">Deductibles & Limits</h4>
      <div class="grid grid-cols-2 gap-3">
        <div class="p-3 bg-blue-950/20 rounded-xl border border-blue-900/30">
          <span class="text-xs text-slate-400 block font-medium">In-Network Ded.</span>
          <span class="text-lg font-bold text-electric-blue block leading-tight">${financials.in_network_deductible?.amount || 'N/A'}</span>
          <span class="text-[10px] text-slate-500 leading-tight">${financials.in_network_deductible?.nuance || ''}</span>
        </div>
        <div class="p-3 bg-slate-900/40 rounded-xl border border-slate-800/80">
          <span class="text-xs text-slate-400 block font-medium">OOP Max</span>
          <span class="text-lg font-bold text-slate-200 block leading-tight">${financials.out_of_pocket_max?.amount || 'N/A'}</span>
          <span class="text-[10px] text-slate-500 leading-tight">${financials.out_of_pocket_max?.nuance || ''}</span>
        </div>
      </div>
    </div>

    <!-- Routine Care costs -->
    <div class="space-y-3">
      <h4 class="text-xs font-bold text-slate-500 tracking-wider uppercase">Routine Care Co-shares</h4>
      <div class="space-y-2">
        <div class="flex justify-between items-center p-2.5 bg-slate-900/25 hover:bg-slate-800/55 rounded-lg border border-slate-900 transition-colors text-xs font-medium">
          <span class="text-slate-400">Preventive Care</span>
          <span class="text-slate-200 font-bold">${routineCare.preventive_care?.cost || 'N/A'}</span>
        </div>
        <div class="flex justify-between items-center p-2.5 bg-slate-900/25 hover:bg-slate-800/55 rounded-lg border border-slate-900 transition-colors text-xs font-medium">
          <span class="text-slate-400">Primary Care Visit</span>
          <span class="text-slate-200 font-bold">${routineCare.primary_care?.cost || 'N/A'}</span>
        </div>
        <div class="flex justify-between items-center p-2.5 bg-slate-900/25 hover:bg-slate-800/55 rounded-lg border border-slate-900 transition-colors text-xs font-medium">
          <span class="text-slate-400">Specialist Visit</span>
          <span class="text-slate-200 font-bold">${routineCare.specialist?.cost || 'N/A'}</span>
        </div>
      </div>
    </div>

    <!-- Prior Auth Checklist -->
    <div class="space-y-3">
      <h4 class="text-xs font-bold text-slate-500 tracking-wider uppercase">Requires Prior Auth</h4>
      <div class="space-y-2">
        ${priorAuth.length > 0 ? priorAuth.map(item => `
          <div class="p-3 bg-amber-950/20 rounded-xl border border-amber-900/30 text-xs">
            <span class="font-bold text-amber-400 block">${item.service || 'N/A'}</span>
            <p class="text-slate-400 mt-1 leading-relaxed">${item.details || ''}</p>
            <span class="text-[10px] text-amber-500 font-semibold block mt-1.5">Cite: ${item.citation || 'N/A'}</span>
          </div>
        `).join('') : '<p class="text-xs text-slate-500 italic">No prior authorizations found.</p>'}
      </div>
    </div>

    <!-- Exclusions Checklist -->
    <div class="space-y-3">
      <h4 class="text-xs font-bold text-slate-500 tracking-wider uppercase text-rose-500">Major Exclusions</h4>
      <div class="space-y-2">
        ${exclusions.length > 0 ? exclusions.map(item => `
          <div class="p-3 bg-rose-950/20 rounded-xl border border-rose-900/30 text-xs">
            <span class="font-bold text-rose-400 block">${item.exclusion || 'N/A'}</span>
            <p class="text-slate-400 mt-1 leading-relaxed">${item.explanation || ''}</p>
            <span class="text-[10px] text-rose-500 font-semibold block mt-1.5">Cite: ${item.citation || 'N/A'}</span>
          </div>
        `).join('') : '<p class="text-xs text-slate-500 italic">No explicit exclusions found.</p>'}
      </div>
    </div>
  `;
}

function toggleSnapshot(forceOpen = null) {
  const panel = document.getElementById('policy-snapshot-panel');
  if (forceOpen !== null) {
    isSnapshotOpen = forceOpen;
  } else {
    isSnapshotOpen = !isSnapshotOpen;
  }
  
  if (isSnapshotOpen) {
    panel.classList.remove('collapsed');
  } else {
    panel.classList.add('collapsed');
  }
}

// Conversation Handling
function submitPrompt(text) {
  document.getElementById('chat-input').value = text;
  sendMessage();
}

function handleInputKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

function selectOnboardingCard(index) {
  let promptText = '';
  if (index === 0) promptText = "Is my knee surgery covered under this policy?";
  if (index === 1) promptText = "Summarize my policy in simple terms.";
  if (index === 2) promptText = "Explain this section of my policy in plain English.";
  if (index === 3) promptText = "What are the most important exclusions I should know about?";
  
  // Fast finish onboarding without default home transition
  skipOnboarding(false);
  
  // Trigger mock policy registration without auto transition
  policyName = "Standard_Choice_Policy.pdf";
  policyId = uuidv4();
  
  transitionToAnalysisMode(null, null);
  
  // Set chat input and trigger transition directly to conversation
  document.getElementById('chat-input').value = promptText;
  transitionToState('conversation');
  sendMessage();
}

function sendMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  
  if (currentAppState !== 'conversation') {
    transitionToState('conversation');
  }
  
  // Clear starter prompts chips
  const chips = document.getElementById('starter-prompt-chips');
  if (chips) {
    chips.classList.add('hidden');
  }
  
  // Add User Message
  appendChatMessage(text, 'user');
  input.value = '';
  
  // Scroll chat
  scrollChatToBottom();
  
  // Add Mike typing indicator
  const typId = appendTypingIndicator();
  
  const payload = {
    question_text: text,
    scenario_context: null,
    requested_decision_type: "coverage",
    session_id: null,
    client_request_id: null
  };

  fetch(`/v1/policies/${policyId}/coverage/evaluations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Evaluation failed with status ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    removeTypingIndicator(typId);
    renderMikeResponse(data);
    scrollChatToBottom();
  })
  .catch(err => {
    console.warn("Backend evaluation request failed, using local mock response:", err);
    showSystemToast("Backend offline or missing API key. Loading fallback response.");
    
    setTimeout(() => {
      removeTypingIndicator(typId);
      renderMikeResponse(mockCoverageResponse);
      scrollChatToBottom();
    }, 1000);
  });
}

function appendChatMessage(text, sender) {
  const list = document.getElementById('messages-list');
  const container = document.createElement('div');
  
  if (sender === 'user') {
    container.className = "flex justify-end w-full";
    container.innerHTML = `
      <div class="chat-bubble-user px-4 py-3 rounded-3xl max-w-lg shadow-sm text-sm leading-relaxed">
        ${text}
      </div>
    `;
  } else {
    container.className = "flex justify-start w-full";
    container.innerHTML = `
      <div class="chat-bubble-mike p-5 rounded-3xl max-w-xl shadow-sm leading-relaxed flex space-x-3">
        <div class="w-8 h-8 rounded-xl bg-blue-950/40 text-electric-blue flex items-center justify-center shrink-0 border border-blue-900/40">
          <i data-lucide="bot" class="w-4.5 h-4.5"></i>
        </div>
        <div class="flex-1 flex flex-col text-sm text-slate-200">
          ${text}
        </div>
      </div>
    `;
  }
  
  list.appendChild(container);
  lucide.createIcons();
}

function appendTypingIndicator() {
  const list = document.getElementById('messages-list');
  const container = document.createElement('div');
  const id = `typing-${Date.now()}`;
  container.id = id;
  container.className = "flex justify-start w-full transition-opacity duration-300";
  container.innerHTML = `
    <div class="chat-bubble-mike px-5 py-4.5 rounded-3xl max-w-xs shadow-sm flex items-center space-x-3">
      <div class="w-8 h-8 rounded-xl bg-blue-950/40 text-electric-blue flex items-center justify-center shrink-0 border border-blue-900/40">
        <i data-lucide="bot" class="w-4.5 h-4.5"></i>
      </div>
      <div class="flex space-x-1 pl-1">
        <div class="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
        <div class="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
        <div class="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
      </div>
    </div>
  `;
  list.appendChild(container);
  lucide.createIcons();
  return id;
}

function removeTypingIndicator(id) {
  const node = document.getElementById(id);
  if (node) node.remove();
}

// Render structured insurance details cleanly
function renderMikeResponse(resp) {
  const list = document.getElementById('messages-list');
  const container = document.createElement('div');
  container.className = "flex justify-start w-full";
  
  const answer = resp?.answer || {};
  const confidence = resp?.confidence || {};
  const citations = resp?.citations || [];
  
  // Decide badge styling
  let badgeHTML = '';
  const decision = answer.decision || '';
  if (decision === 'likely_covered') {
    badgeHTML = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/30 text-emerald-400 border border-emerald-900/50"><i data-lucide="check" class="w-3.5 h-3.5 mr-1"></i> Likely Covered</span>`;
  } else if (decision === 'conditionally_covered') {
    badgeHTML = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-950/30 text-amber-400 border border-amber-900/50"><i data-lucide="alert-circle" class="w-3.5 h-3.5 mr-1"></i> Coverage Uncertain</span>`;
  } else if (decision === 'likely_not_covered') {
    badgeHTML = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-rose-950/30 text-rose-400 border border-rose-900/50"><i data-lucide="x" class="w-3.5 h-3.5 mr-1"></i> Likely Not Covered</span>`;
  } else {
    badgeHTML = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-slate-900/30 text-slate-400 border border-slate-800/50"><i data-lucide="help-circle" class="w-3.5 h-3.5 mr-1"></i> ${decision || 'Cannot Determine'}</span>`;
  }

  const citationsHTML = citations.length > 0 
    ? citations.map((cit, idx) => `
        <div class="border border-slate-800 rounded-2xl overflow-hidden shadow-sm bg-slate-900/20">
          <button onclick="toggleCitationAccordion('cit-acc-${idx}')" class="w-full flex items-center justify-between p-3.5 text-xs font-bold text-slate-300 hover:bg-slate-900/40 focus:outline-none">
            <span class="flex items-center"><i data-lucide="bookmark" class="w-3.5 h-3.5 mr-2 text-electric-blue"></i> ${cit.heading || 'Citation'} — Page ${cit.page_number || 'N/A'}</span>
            <i data-lucide="chevron-down" class="w-4 h-4 text-slate-500"></i>
          </button>
          <div id="cit-acc-${idx}" class="accordion-content">
            <div class="p-4 border-t border-slate-800 text-xs text-slate-400 bg-slate-950/40 leading-relaxed italic select-text">
              "${cit.quoted_text || 'No text quoted.'}"
            </div>
          </div>
        </div>
      `).join('')
    : `<p class="text-xs text-slate-500 italic">No direct citations available in this decision.</p>`;

  const conditions = answer.conditions || [];
  const nextSteps = answer.next_steps || [];
  const grounding = confidence.policy_grounding_status || 'N/A';

  container.innerHTML = `
    <div class="chat-bubble-mike p-5 rounded-3xl max-w-xl shadow-sm leading-relaxed flex space-x-3 w-full animate-fade-in">
      <div class="w-8 h-8 rounded-xl bg-blue-950/40 text-electric-blue flex items-center justify-center shrink-0 border border-blue-900/40">
        <i data-lucide="bot" class="w-4.5 h-4.5"></i>
      </div>
      <div class="flex-1 flex flex-col text-sm text-slate-200 space-y-4">
        
        <!-- Badge -->
        <div class="flex items-center justify-between">
          ${badgeHTML}
          <span class="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Grounding: ${grounding}</span>
        </div>

        <!-- Short answer -->
        <p class="font-bold text-slate-200 text-sm leading-snug">${answer.short_answer || 'No summary response.'}</p>
        
        <!-- Detailed reasoning -->
        <p class="text-xs leading-relaxed text-slate-400">${answer.detailed_reasoning || ''}</p>

        <!-- Conditions & Next Steps -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <h5 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Conditions</h5>
            <ul class="space-y-1.5 text-xs text-slate-400 font-medium">
              ${conditions.length > 0 
                ? conditions.map(c => `<li class="flex items-start"><i data-lucide="chevron-right" class="w-3.5 h-3.5 mr-1 text-slate-500 shrink-0 mt-0.5"></i> ${c}</li>`).join('') 
                : '<li class="text-slate-500 italic">None specified</li>'}
            </ul>
          </div>
          <div>
            <h5 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Next Steps</h5>
            <ul class="space-y-1.5 text-xs text-slate-400 font-medium">
              ${nextSteps.length > 0 
                ? nextSteps.map(s => `<li class="flex items-start"><i data-lucide="arrow-right-circle" class="w-3.5 h-3.5 mr-1 text-electric-blue shrink-0 mt-0.5"></i> ${s}</li>`).join('') 
                : '<li class="text-slate-500 italic">None specified</li>'}
            </ul>
          </div>
        </div>

        <!-- Citations Accordion -->
        <div class="space-y-2 pt-2">
          <h5 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Policy Citations</h5>
          ${citationsHTML}
        </div>

      </div>
    </div>
  `;
  
  list.appendChild(container);
  lucide.createIcons();
}

function toggleCitationAccordion(id) {
  const content = document.getElementById(id);
  content.classList.toggle('expanded');
}

function scrollChatToBottom() {
  const scrollable = document.getElementById('chat-messages-container');
  scrollable.scrollTop = scrollable.scrollHeight;
}

// Helpers
function showSystemToast(msg) {
  const toast = document.createElement('div');
  toast.className = "fixed bottom-8 left-[50%] -translate-x-1/2 bg-slate-900/90 backdrop-blur text-white py-3 px-6 rounded-full text-xs font-bold shadow-2xl z-50 transition-all transform scale-90 opacity-0 duration-500 pointer-events-none";
  toast.innerText = msg;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.remove('opacity-0', 'scale-90');
    toast.classList.add('scale-100');
  }, 100);
  
  setTimeout(() => {
    toast.classList.add('opacity-0', 'scale-90');
    setTimeout(() => toast.remove(), 500);
  }, 4000);
}

function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

// Global keyboard arrow key navigation for accessibility
window.addEventListener('keydown', (e) => {
  const activeEl = document.activeElement;
  if (!activeEl) return;
  
  const onboardingContainer = document.getElementById('onboarding-cards');
  const onboardingCards = onboardingContainer ? Array.from(onboardingContainer.querySelectorAll('button')) : [];
  const onboardingIndex = onboardingCards.indexOf(activeEl);
  
  const chipsContainer = document.getElementById('starter-prompt-chips');
  const promptChips = chipsContainer ? Array.from(chipsContainer.querySelectorAll('button')) : [];
  const chipIndex = promptChips.indexOf(activeEl);
  
  if (onboardingIndex !== -1) {
    let nextIndex = onboardingIndex;
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      if (onboardingIndex === 0) nextIndex = 1;
      else if (onboardingIndex === 2) nextIndex = 3;
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      if (onboardingIndex === 1) nextIndex = 0;
      else if (onboardingIndex === 3) nextIndex = 2;
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (onboardingIndex === 0) nextIndex = 2;
      else if (onboardingIndex === 1) nextIndex = 3;
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (onboardingIndex === 2) nextIndex = 0;
      else if (onboardingIndex === 3) nextIndex = 1;
    } else if (e.key === 'Enter') {
      e.preventDefault();
      selectOnboardingCard(onboardingIndex);
    }
    
    if (nextIndex !== onboardingIndex && onboardingCards[nextIndex]) {
      onboardingCards[nextIndex].focus();
    }
  } else if (chipIndex !== -1) {
    let nextIndex = chipIndex;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      nextIndex = (chipIndex + 1) % promptChips.length;
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      nextIndex = (chipIndex - 1 + promptChips.length) % promptChips.length;
    } else if (e.key === 'Enter') {
      e.preventDefault();
      activeEl.click();
    }
    
    if (nextIndex !== chipIndex && promptChips[nextIndex]) {
      promptChips[nextIndex].focus();
    }
  }
});
