# Mike

## The Problem and an Overview

We live in a world with so many diseases, with so many treatments, but as medicine rises, so do the costs. We pivot to using
health insurance to cover the costs, but insurance companies are for-profit, and they have to make money. The contracts are 
complex, Users never properly understand them and they are often surprised by the bills, and the denials that occur. We all know 
the shock of a denial, and seeing a clause in the contract which you didn't know about, The panic sets in, and knowing what to do
next is a nightmare. Mike is an AI powered Health insurance Navigator that helps users undestand their policies, evaluate their
coverages for real world situation and navigate claim denials with Evidence-backed guidance.

## Overview of Mike, it's current state and what the Vision we hope for

Millions of People purchase health insurance without truly understand what is covering, what is excluded, or what happens when
a claim is denied. Mike is an AI powered Health insurance Navigator that helps users undestand their policies, evaluate their
coverages for real world situation and navigate claim denials with Evidence-backed guidance. 

Instead of Discovering policy limitations during a medical emergency, users can understand their coverage before treatment, 
understand why claims were denied, and determine their next best action. 
It aims to transform legal contracts into actionable decisions. 

The current vision for Mike remains to provide legal aid to users, without the need for a lawyer, I want to expand this beyond 
health insurance, to other insurances, and what commonly pains everyday people, such as rental agreements, or even convoluted traffic tickets. The vision is to empower users to understand their legal rights, their agreements, and to navigate the legal 
system with confidence, and not be taken advantage of by the complexity of legalese.

### Core functionalies Currently decided.
1. **Policy Understanding**: Users can upload their health insurance policy documents, and Mike will parse the document, extract key information, and provide a user-friendly summary of the coverage, exclusions, and important clauses. It is going to be parsed
into section wise details, which will be expandable, then the user will able to chat with it to ask questions about the policy, and get specific answers based on the document. I also might wanna expand to allowing the user to upload other policies to even compare them.
2. **Coverage Evaluation**: Users can input real-world scenarios, such as "I have a headache, and I want to go to the doctor, will my insurance cover it?" Mike will evaluate the scenario against the user's policy and provide an answer based on the coverage details. It will also provide a confidence score for the answer, and if the confidence is low, it will suggest the user to consult with a human expert. It will get relevant clauses, explain the conditions, explain the risks and longterm implications of the decision, explain the missing requirements and what you need.
3. **Claim Denial Navigation**: If a user's claim is denied, they can input the denial reason, and Mike will analyze the denial against the policy, and provide evidence-backed guidance on how to appeal the denial, what arguments to make, and what evidence to gather. It will also provide a step-by-step guide on how to navigate the appeals process. It will provide their current reasoning, relevant clauses, and the evidence they need to gather, and the arguments they can make, and the next steps to take,
and even maybe allowing for appeal draft generation.