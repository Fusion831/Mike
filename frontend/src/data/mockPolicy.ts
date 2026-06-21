import { Artifact, ChatMessage } from '../types';

export const mockArtifacts: Artifact[] = [
  {
    id: 'meet-your-policy',
    name: 'Meet Your Policy',
    type: 'policy_summary',
    version: '2026.1',
    lastUpdated: '2026-06-21',
    preview: {
      badge: 'Policy Overview',
      heroStat: 'Gold PPO',
      secondaryStat: 'BCBS Network',
      shortDescription: 'A Gold-tier plan with broad network access. You do not need specialist referrals, but using out-of-network care increases costs.',
      quickAction: {
        id: 'qa-doctor-network',
        label: "Check my doctor's network",
        type: 'chat_prompt',
        payload: 'Is my current doctor in the Blue Cross Blue Shield network?'
      }
    },
    sections: [
      {
        id: 'overview-gold-ppo',
        title: 'Overview of Gold PPO',
        content: 'A PPO gives you the freedom to see any provider you want. You do not need a Primary Care Physician to write referrals for specialist appointments.',
        citations: ['Section 1.4 - Access to Care']
      },
      {
        id: 'network-cost-sharing',
        title: 'Network Cost Sharing',
        content: 'Network doctors have agreed to discounted rates. Out-of-network doctors can balance-bill you for the difference, which means you pay much more.',
        citations: ['Section 11.1 - Network Cost Sharing']
      }
    ],
    deepCTAs: [
      {
        id: 'dc-specialist-referral',
        label: 'Ask Mike: Is my current specialist in-network?',
        type: 'chat_prompt',
        payload: 'Is my specialist covered under the BCBS PPO network?'
      }
    ]
  },
  {
    id: 'your-share-of-costs',
    name: 'Your Share of Costs',
    type: 'policy_summary',
    version: '2026.1',
    lastUpdated: '2026-06-21',
    preview: {
      badge: 'Plan Financials',
      heroStat: '$750',
      secondaryStat: 'In-Network Deductible',
      shortDescription: 'You pay the first $750 of hospital/specialist care yourself. Once you hit the $4,500 Out-of-Pocket limit, plan pays 100%.',
      quickAction: {
        id: 'qa-deductible-progress',
        label: 'Check my deductible rules',
        type: 'chat_prompt',
        payload: 'What services count towards meeting my $750 deductible?'
      }
    },
    sections: [
      {
        id: 'understanding-deductible',
        title: 'Understanding the Deductible',
        content: 'Your $750 deductible applies to hospital stays, surgeries, and high-tech imaging. It is waived for preventative visits and your first 3 doctor visits.',
        citations: ['Section 2.1 - Deductibles']
      },
      {
        id: 'out-of-pocket-max',
        title: 'Out-of-Pocket Maximum',
        content: 'Once you spend $4,500 total on deductibles, copays, and coinsurance, Aegis pays 100% of all in-network care for the rest of the year.',
        citations: ['Section 2.3 - OOP Max']
      }
    ],
    deepCTAs: [
      {
        id: 'dc-oop-estimate',
        label: 'Ask Mike: Calculate my out-of-pocket surgery estimate',
        type: 'chat_prompt',
        payload: 'Estimate my out-of-pocket expenses for outpatient surgery under this plan.'
      }
    ]
  },
  {
    id: 'getting-claims-approved',
    name: 'Getting Claims Approved',
    type: 'policy_summary',
    version: '2026.1',
    lastUpdated: '2026-06-21',
    preview: {
      badge: 'Coverage Guidelines',
      heroStat: '5 Key Rules',
      secondaryStat: 'Notification & Filing',
      shortDescription: 'Important rules regarding emergency notification times and timely filing deadlines to ensure your claims get paid.',
      quickAction: {
        id: 'qa-prevent-billing',
        label: 'How to prevent billing issues',
        type: 'chat_prompt',
        payload: 'What are the main reasons insurance claims get denied under this plan?'
      }
    },
    sections: [
      {
        id: 'emergency-notification',
        title: 'Emergency Notification Window',
        content: 'You must notify Aegis within 48 hours of any emergency hospital admission to ensure full coverage.',
        citations: ['Section 3.5 - Emergency Admissions']
      },
      {
        id: 'ancillary-trap',
        title: 'The Out-of-Network Assistant Risk',
        content: 'Even at an in-network hospital, the anesthesiologist who assists with your surgery may be out-of-network. Ask to verify this before surgery.',
        citations: ['Section 11.2 - Ancillary Providers']
      }
    ],
    deepCTAs: [
      {
        id: 'dc-confirm-team',
        label: 'Ask Mike: How to ensure all my surgical team is in-network',
        type: 'chat_prompt',
        payload: 'How do I check if my anesthesiologist and surgeons are in-network before scheduling care?'
      }
    ]
  },
  {
    id: 'before-treatment',
    name: 'Before Treatment',
    type: 'policy_summary',
    version: '2026.1',
    lastUpdated: '2026-06-21',
    preview: {
      badge: 'Approvals',
      heroStat: '8 Categories',
      secondaryStat: 'Prior Authorization',
      shortDescription: 'Services that must be approved in advance by the insurer clinical review board before booking treatment.',
      quickAction: {
        id: 'qa-check-approval',
        label: 'Check if my care needs approval',
        type: 'chat_prompt',
        payload: 'Which healthcare services require prior authorization under my plan?'
      }
    },
    sections: [
      {
        id: 'high-tech-imaging',
        title: 'High-Tech Imaging Approvals',
        content: 'All MRI, CT, and PET scans require clinical pre-approval, except in emergency room settings.',
        citations: ['Section 4.2 - High-Tech Imaging']
      },
      {
        id: 'rehab-therapy',
        title: 'Rehabilitative Therapy Limits',
        content: 'You get 6 physical therapy sessions automatically. Session 7 and beyond require a clinical review showing progress.',
        citations: ['Section 6.5 - Rehabilitative Care']
      }
    ],
    deepCTAs: [
      {
        id: 'dc-verify-mri',
        label: 'Ask Mike: Verify if my MRI requires pre-approval',
        type: 'chat_prompt',
        payload: 'Do I need prior authorization to get an MRI done for back pain?'
      }
    ]
  },
  {
    id: 'when-coverage-doesnt-apply',
    name: "When Coverage Doesn't Apply",
    type: 'policy_summary',
    version: '2026.1',
    lastUpdated: '2026-06-21',
    preview: {
      badge: 'Exclusions',
      heroStat: '8 Exclusions',
      secondaryStat: 'Not Covered',
      shortDescription: 'Services that this policy absolutely will not pay for, regardless of medical necessity, such as adult dental/vision.',
      quickAction: {
        id: 'qa-search-excluded',
        label: 'Search excluded services',
        type: 'chat_prompt',
        payload: 'What medical services are completely excluded from my plan?'
      }
    },
    sections: [
      {
        id: 'cosmetic-procedures',
        title: 'Cosmetic & Plastic Surgery',
        content: 'Cosmetic procedures are excluded unless reconstructive surgery is required following an accidental injury.',
        citations: ['Section 12.3 - Cosmetic Exclusions']
      },
      {
        id: 'dental-vision-carveout',
        title: 'Adult Dental & Vision',
        content: 'Standard cleanings, fillings, frames, and eye exams are not covered. Requires a separate policy.',
        citations: ['Section 12.8 - Vision/Dental Limitations']
      }
    ],
    deepCTAs: [
      {
        id: 'dc-dental-emergencies',
        label: 'Ask Mike: Are dental surgeries covered in emergencies?',
        type: 'chat_prompt',
        payload: 'If I have an emergency jaw injury, does my PPO plan cover dental surgery?'
      }
    ]
  },
  {
    id: 'everyday-healthcare',
    name: 'Everyday Healthcare',
    type: 'policy_summary',
    version: '2026.1',
    lastUpdated: '2026-06-21',
    preview: {
      badge: 'Routine Care',
      heroStat: '$25',
      secondaryStat: 'Primary Care Copay',
      shortDescription: 'Quick reference for routine doctor visits, urgent care, and emergency room visits, with waived deductibles.',
      quickAction: {
        id: 'qa-compare-copays',
        label: 'Compare visit copays',
        type: 'chat_prompt',
        payload: 'What are my copays for primary care, specialists, and urgent care?'
      }
    },
    sections: [
      {
        id: 'doctor-office-visits',
        title: 'Doctor Visits',
        content: 'Primary care visits cost a flat $25 copay (deductible waived for first 3 visits). Specialists cost a flat $50 copay.',
        citations: ['Section 1.5 - Office Visits']
      },
      {
        id: 'er-and-urgent-care',
        title: 'Emergency Room & Urgent Care',
        content: 'Urgent care is a flat $45 copay. Emergency room is a $250 copay (waived if admitted to hospital within 24 hours).',
        citations: ['Section 5.1 - ER Services']
      }
    ],
    deepCTAs: [
      {
        id: 'dc-check-pt-copay',
        label: 'Ask Mike: Check copay for physical therapy office visits',
        type: 'chat_prompt',
        payload: 'How much do I pay per session for a physical therapy specialist visit?'
      }
    ]
  },
  {
    id: 'medication-pricing-tiers',
    name: 'Medication Pricing Tiers',
    type: 'policy_summary',
    version: '2026.1',
    lastUpdated: '2026-06-21',
    preview: {
      badge: 'Pharmacy',
      heroStat: 'Tier 1: $10',
      secondaryStat: 'Generic Drugs',
      shortDescription: 'Plan groups medications into 4 shelves. Ask your doctor for Tier 1 generics to keep your costs low.',
      quickAction: {
        id: 'qa-search-prescription',
        label: 'Search my prescriptions',
        type: 'chat_prompt',
        payload: 'How are prescription drugs categorized and priced in my plan?'
      }
    },
    sections: [
      {
        id: 'tier-1-tier-2',
        title: 'Tier 1 and Tier 2 Medications',
        content: 'Tier 1 Generics cost $10 copay. Tier 2 Preferred Brands cost $35 copay. Neither requires prior authorization.',
        citations: ['Section 10.1 - Formulary']
      },
      {
        id: 'tier-3-tier-4',
        title: 'Tier 3 and Tier 4 Restrictions',
        content: 'Tier 3 Non-Preferred ($70) requires step therapy (trying two cheaper alternatives first). Tier 4 Specialty (30% coinsurance) requires pre-approval.',
        citations: ['Section 10.3 - Step Therapy']
      }
    ],
    deepCTAs: [
      {
        id: 'dc-step-therapy',
        label: 'Ask Mike: How does step therapy work?',
        type: 'chat_prompt',
        payload: 'What are the rules and process for step therapy drug approvals?'
      }
    ]
  },
  {
    id: 'real-life-examples',
    name: 'Real-Life Examples',
    type: 'policy_summary',
    version: '2026.1',
    lastUpdated: '2026-06-21',
    preview: {
      badge: 'Cost Estimates',
      heroStat: '$380',
      secondaryStat: 'Broken Arm Estimate',
      shortDescription: 'Concrete examples of how deductibles and copays combine for common medical situations like a broken arm or childbirth.',
      quickAction: {
        id: 'qa-estimate-treatment',
        label: 'Estimate my treatment cost',
        type: 'chat_prompt',
        payload: 'Show me examples of out-of-pocket costs for a medical procedure.'
      }
    },
    sections: [
      {
        id: 'broken-arm-scenario',
        title: 'Broken Arm Emergency Estimate',
        content: 'Estimated total user cost: $380. Includes a $250 ER copay plus 20% coinsurance on X-ray imaging ($130) once deductible is met.',
        citations: ['Section 3.4 - Emergency Services']
      },
      {
        id: 'childbirth-scenario',
        title: 'Childbirth Hospital Estimate',
        content: 'Estimated total user cost: $1,800. Includes $750 deductible plus 20% coinsurance on delivery fees.',
        citations: ['Section 3.2 - Maternity Benefits']
      }
    ],
    deepCTAs: [
      {
        id: 'dc-estimate-knee',
        label: 'Ask Mike: Calculate out-of-pocket costs for knee surgery',
        type: 'chat_prompt',
        payload: 'Can you show me the cost breakdown for outpatient knee surgery?'
      }
    ]
  }
];

export const mockResponseFlow = (prompt: string): ChatMessage => {
  const query = prompt.toLowerCase();
  
  if (query.includes('mri') || query.includes('imaging') || query.includes('approval') || query.includes('pre-approval')) {
    return {
      id: `mike-msg-${Date.now()}`,
      sender: 'mike',
      text: "Yes, diagnostic MRIs are likely covered under your plan, but they require a **Pre-Care Approval** before you schedule them.",
      decision: 'conditionally_covered',
      detailedReasoning: "Under Aegis Care Plus PPO, high-tech imaging services (such as MRIs, CT scans, and PET scans) are covered at 80% in-network after your deductible is met. However, prior clinical approval must be secured by your ordering physician. Services received without approval are subject to a 50% benefit reduction penalty.",
      conditions: [
        "Must be ordered by an in-network specialist",
        "Clinical necessity notes must be sent to Aegis review board",
        "Pre-approval must be obtained at least 5 business days in advance"
      ],
      nextSteps: [
        "Ask your doctor to submit the pre-certification form to Aegis",
        "Confirm the imaging facility is fully in-network",
        "Call Aegis Member Services to verify approval code before your appointment"
      ],
      referencedArtifactIds: ['before-treatment', 'your-share-of-costs']
    };
  }

  if (query.includes('cost') || query.includes('deductible') || query.includes('pay') || query.includes('limit')) {
    return {
      id: `mike-msg-${Date.now()}`,
      sender: 'mike',
      text: "Your plan features a **$750 In-Network Deductible** and a **$4,500 Out-of-Pocket Maximum**.",
      decision: 'likely_covered',
      detailedReasoning: "You will pay 100% of the discounted insurer rates for specialist care and hospital services until your $750 deductible is met. Once met, Aegis covers 80% of costs (you pay 20% coinsurance) for in-network care. If your total out-of-pocket costs reach $4,500, Aegis pays 100% of all covered in-network services.",
      conditions: [
        "Deductible applies per individual per calendar year",
        "Preventive visits do not require meeting the deductible",
        "Out-of-network deductible is separate ($2,500)"
      ],
      nextSteps: [
        "Check your current deductible balance on the Aegis portal",
        "Ensure providers file claims directly to Aegis",
        "Keep receipts of copays as they count towards your Out-of-Pocket Max"
      ],
      referencedArtifactIds: ['your-share-of-costs', 'everyday-healthcare']
    };
  }

  if (query.includes('exclusion') || query.includes('not covered') || query.includes('dental') || query.includes('vision')) {
    return {
      id: `mike-msg-${Date.now()}`,
      sender: 'mike',
      text: "Standard adult dental, vision, and cosmetic surgeries are **completely excluded** from this policy.",
      decision: 'likely_not_covered',
      detailedReasoning: "Aegis Care Plus does not provide benefits for cosmetic procedures (unless reconstructive following an accident), routine adult dental work, cleanings, or vision exams/frames. To cover these services, you must purchase standalone dental or vision riders.",
      conditions: [
        "Accidental reconstructive surgery requires notification within 72 hours",
        "Pediatric dental/vision is covered up to age 19"
      ],
      nextSteps: [
        "Check if you have purchased secondary dental/vision riders",
        "Inquire about dental discount plans if self-paying",
        "Consult your surgeon to confirm your procedure is deemed medical, not cosmetic"
      ],
      referencedArtifactIds: ['when-coverage-doesnt-apply']
    };
  }

  // General default answer
  return {
    id: `mike-msg-${Date.now()}`,
    sender: 'mike',
    text: "I can help clarify that based on your Aegis PPO contract. Let's look at the coverage details.",
    decision: 'likely_covered',
    detailedReasoning: "This Aegis Gold PPO plan offers comprehensive network coverage for medical needs. Most clinical services are paid at 80% in-network after your $750 deductible, while routine visits only require a flat copay.",
    conditions: [
      "Must seek care from Aegis contracted providers for lowest rates",
      "Prior approvals apply to high-tech imaging and inpatient stays"
    ],
    nextSteps: [
      "Review the specific 'Before Treatment' card on the right",
      "Ask a more detailed question about a specific treatment"
    ],
    referencedArtifactIds: ['meet-your-policy', 'everyday-healthcare']
  };
};
