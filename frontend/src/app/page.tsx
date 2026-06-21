"use client";

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useDragControls } from 'framer-motion';
import { 
  Bot, 
  User, 
  Send, 
  FileText, 
  Check, 
  Plus, 
  Sparkles, 
  ChevronRight, 
  ChevronLeft, 
  ChevronDown,
  LayoutGrid, 
  Layers, 
  ShieldAlert, 
  ArrowRight,
  HelpCircle,
  X,
  FileSpreadsheet,
  AlertCircle,
  FileCheck,
  CheckCircle2,
  Bookmark
} from 'lucide-react';
import { mockArtifacts, mockResponseFlow } from '../data/mockPolicy';
import { Artifact, ChatMessage } from '../types';

export default function Page() {
  // Navigation & Core States
  const [currentTab, setCurrentTab] = useState<'home' | 'defense'>('home');
  const [viewState, setViewState] = useState<'upload' | 'discovery' | 'workspace'>('upload');
  const [deckLayout, setDeckLayout] = useState<'stack' | 'grid'>('stack');
  const [policyName, setPolicyName] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  
  // Card Stack States
  const [currentCardIndex, setCurrentCardIndex] = useState<number>(0);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);
  
  // Expanded sections for accordions: artifactId_sectionId -> boolean
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  
  // Chat States
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState<string>('');
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [showStarterChips, setShowStarterChips] = useState<boolean>(true);
  
  // Highlighting & Soft Focus States
  const [highlightedReference, setHighlightedReference] = useState<{
    artifactId: string;
    sectionId?: string;
  } | null>(null);

  // Refs for scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const artifactRefs = useRef<Record<string, HTMLDivElement | null>>({});

  // 1. Ingestion File Upload Simulation
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    simulateUpload(file.name);
  };

  const simulateUpload = (name: string) => {
    setIsUploading(true);
    setUploadProgress(0);
    setPolicyName(name);
    
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setIsUploading(false);
            setViewState('discovery');
          }, 400);
          return 100;
        }
        return prev + 10;
      });
    }, 120);
  };

  // 2. Navigation Actions
  const handleQuickAction = (artifact: Artifact) => {
    const action = artifact.preview.quickAction;
    triggerChatQuery(action.payload, [artifact.id]);
  };

  const handleDeepAction = (actionPayload: string, artifactId: string) => {
    triggerChatQuery(actionPayload, [artifactId]);
  };

  const triggerChatQuery = (queryText: string, referencedIds: string[]) => {
    setViewState('workspace');
    setShowStarterChips(false);
    
    // Add user message
    const userMsg: ChatMessage = {
      id: `user-msg-${Date.now()}`,
      sender: 'user',
      text: queryText
    };
    
    setChatHistory((prev) => [...prev, userMsg]);
    setIsTyping(true);
    
    // Simulate Mike response
    setTimeout(() => {
      const response = mockResponseFlow(queryText);
      response.referencedArtifactIds = referencedIds;
      setChatHistory((prev) => [...prev, response]);
      setIsTyping(false);
      
      // Auto-open the referenced card
      if (referencedIds.length > 0) {
        setActiveArtifactId(referencedIds[0]);
      }
    }, 1200);
  };

  const handleSendMessage = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatInput.trim()) return;

    const query = chatInput;
    setChatInput('');
    triggerChatQuery(query, []);
  };

  // 3. Deep Link & Soft Focus Sequence
  const handleCitationClick = (artifactId: string, sectionId?: string) => {
    // Scroll to the artifact on the right
    const el = artifactRefs.current[artifactId];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Open the card in the list
    setActiveArtifactId(artifactId);
    
    // Expand the specific section if provided
    if (sectionId) {
      setExpandedSections((prev) => ({
        ...prev,
        [`${artifactId}_${sectionId}`]: true
      }));
    }
    
    // Apply soft focus visual highlight
    setHighlightedReference({ artifactId, sectionId });
    
    // Clear highlight after the 3000ms duration (glow fade)
    setTimeout(() => {
      setHighlightedReference(null);
    }, 3000);
  };

  // Keep chat scrolled to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isTyping]);

  // Keyboard navigation for Wallet Stack
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (viewState !== 'discovery' || deckLayout !== 'stack') return;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        setCurrentCardIndex((prev) => Math.min(prev + 1, mockArtifacts.length - 1));
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        setCurrentCardIndex((prev) => Math.max(prev - 1, 0));
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [viewState, deckLayout]);

  return (
    <div className="flex-1 flex flex-col relative w-full overflow-hidden animated-gradient select-none">
      
      {/* Top Header Segmented Controls */}
      <header className="w-full flex justify-between items-center py-5 px-6 md:px-12 shrink-0 z-30 border-b border-white/5 bg-[#050816]/40 backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-yellow-500 to-amber-600 flex items-center justify-center text-black font-extrabold shadow-md shadow-yellow-500/10">
            M
          </div>
          <span className="font-serif text-lg font-bold tracking-wide text-white">Mike</span>
        </div>

        <div className="relative bg-white/[0.04] backdrop-blur-lg rounded-full p-1 flex space-x-1 border border-white/10 max-w-[280px] w-full">
          <button 
            onClick={() => setCurrentTab('home')}
            className={`flex-1 py-1.5 rounded-full text-xs font-bold transition-all ${
              currentTab === 'home' 
                ? 'bg-white text-slate-900 shadow-md' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Home
          </button>
          <button 
            onClick={() => setCurrentTab('defense')}
            className={`flex-1 py-1.5 rounded-full text-xs font-bold transition-all ${
              currentTab === 'defense' 
                ? 'bg-white text-slate-900 shadow-md' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Claim Defense
          </button>
        </div>

        <div className="flex items-center space-x-3">
          {policyName && (
            <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
              <Check className="w-3.5 h-3.5" />
              <span>{policyName} Loaded</span>
            </div>
          )}
        </div>
      </header>

      {/* Main Workspace Frame */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-6 md:px-12 py-6 flex overflow-hidden relative">
        <AnimatePresence mode="wait">
          
          {/* ==========================================
               CLAIM DEFENSE VIEW (COMING SOON STATE)
               ========================================== */}
          {currentTab === 'defense' && (
            <motion.div 
              key="defense-tab"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="flex-1 flex flex-col justify-center items-center max-w-xl mx-auto h-full text-center select-none"
            >
              <div className="w-20 h-20 bg-blue-950/20 text-blue-400 rounded-3xl flex items-center justify-center mb-6 shadow-lg border border-blue-900/30">
                <ShieldAlert className="w-10 h-10" />
              </div>
              <h2 className="text-2xl font-serif font-bold text-slate-100 mb-2">Claim Defense</h2>
              <p className="text-slate-400 text-sm mb-8 leading-relaxed max-w-md font-medium">
                Upload a claim denial letter from your health insurer. Mike will cross-reference the denial codes with your policy documents to identify contradictions and prepare a structured appeal argument.
              </p>
              
              <div className="w-full border border-dashed border-slate-800 rounded-3xl p-10 bg-slate-950/20 flex flex-col items-center cursor-not-allowed opacity-60">
                <Plus className="w-8 h-8 text-slate-600 mb-3" />
                <span className="text-xs font-bold text-slate-500 tracking-wider uppercase">Coming in Next Release</span>
              </div>
            </motion.div>
          )}

          {/* ==========================================
               HOME TAB WORKFLOWS
               ========================================== */}
          {currentTab === 'home' && (
            <div className="flex-1 flex overflow-hidden h-full">
              
              {/* ── WORKFLOW STATE 1: UPLOAD ── */}
              {viewState === 'upload' && (
                <motion.div 
                  key="upload-view"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 flex flex-col justify-center items-center py-6 max-w-2xl mx-auto w-full select-none"
                >
                  <div className="text-center space-y-3 mb-8">
                    <h1 className="text-4xl md:text-5xl font-serif font-medium text-slate-100 tracking-tight leading-tight">
                      Insurance is confusing.<br />
                      <span className="bg-gradient-to-r from-yellow-500 to-amber-500 bg-clip-text text-transparent">Mike translates.</span>
                    </h1>
                    <p className="text-slate-400 text-sm font-semibold opacity-75 max-w-sm mx-auto">
                      Drop your insurance summary document to organize benefits and check coverage instantly.
                    </p>
                  </div>

                  {/* Dropzone Container */}
                  <div className="w-full glass-panel border border-white/10 rounded-3xl p-12 text-center flex flex-col items-center justify-center shadow-2xl relative overflow-hidden min-h-[300px]">
                    <AnimatePresence>
                      {isUploading ? (
                        <motion.div 
                          key="progress"
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="w-full max-w-xs space-y-4"
                        >
                          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto text-amber-400 border border-amber-500/20">
                            <Bot className="w-8 h-8 animate-pulse" />
                          </div>
                          <div className="space-y-1">
                            <h3 className="text-sm font-bold text-slate-200">Reading policy terms...</h3>
                            <p className="text-xs text-slate-500">Converting medical jargon to simple summaries</p>
                          </div>
                          <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                            <motion.div 
                              className="h-full bg-gradient-to-r from-yellow-500 to-amber-500 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${uploadProgress}%` }}
                              transition={{ duration: 0.1 }}
                            />
                          </div>
                          <span className="text-xs font-bold text-slate-400">{uploadProgress}%</span>
                        </motion.div>
                      ) : (
                        <motion.div 
                          key="idle"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="flex flex-col items-center"
                        >
                          <div className="w-16 h-16 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center justify-center text-slate-400 mb-6 shadow-sm">
                            <FileText className="w-7 h-7" />
                          </div>
                          
                          <label className="cursor-pointer">
                            <span className="px-6 py-3 bg-gradient-to-r from-yellow-500 to-amber-500 hover:from-yellow-600 hover:to-amber-600 text-slate-950 font-bold rounded-2xl shadow-md transition-all inline-flex items-center space-x-2 text-sm">
                              <Plus className="w-4 h-4 text-slate-950 stroke-[3px]" />
                              <span>Select Policy PDF</span>
                            </span>
                            <input 
                              type="file" 
                              accept=".pdf" 
                              className="hidden" 
                              onChange={handleFileUpload} 
                            />
                          </label>

                          <div className="mt-6 text-xs text-slate-500 leading-normal font-medium max-w-xs">
                            Supports summary PPO or HMO policy schedules. Try our demo by selecting any PDF.
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.div>
              )}

              {/* ── WORKFLOW STATE 2: DISCOVERY DECK ── */}
              {viewState === 'discovery' && (
                <motion.div 
                  key="discovery-view"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 flex flex-col justify-between h-full relative"
                >
                  
                  {/* Discovery Deck Title */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 shrink-0 pb-4">
                    <div>
                      <h2 className="text-2xl md:text-3xl font-serif font-medium text-slate-100">
                        Mike found important things about your policy.
                      </h2>
                      <p className="text-xs text-slate-500 mt-1 font-semibold">
                        Browse the key components or skip to workspace questions below.
                      </p>
                    </div>

                    {/* Segmented layout controls */}
                    <div className="bg-white/[0.03] border border-white/5 rounded-xl p-1 flex space-x-1">
                      <button 
                        onClick={() => setDeckLayout('stack')}
                        className={`px-3 py-1.5 rounded-lg flex items-center space-x-2 text-xs font-bold transition-all ${
                          deckLayout === 'stack' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'
                        }`}
                      >
                        <Layers className="w-3.5 h-3.5" />
                        <span>Stack View</span>
                      </button>
                      <button 
                        onClick={() => setDeckLayout('grid')}
                        className={`px-3 py-1.5 rounded-lg flex items-center space-x-2 text-xs font-bold transition-all ${
                          deckLayout === 'grid' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'
                        }`}
                      >
                        <LayoutGrid className="w-3.5 h-3.5" />
                        <span>Grid View</span>
                      </button>
                    </div>
                  </div>

                  {/* Dynamic Layout Rendering */}
                  <div className="flex-1 flex items-center justify-center relative overflow-hidden py-4">
                    {deckLayout === 'stack' ? (
                      
                      /* ── WALLET STACK VIEW ── */
                      <div className="relative w-full max-w-sm h-[380px] flex items-center justify-center">
                        <AnimatePresence>
                          {mockArtifacts.map((artifact, idx) => {
                            // Calculate visible cards in stack (up to 3)
                            const isCurrent = idx === currentCardIndex;
                            const isNext = idx === currentCardIndex + 1;
                            const isPrev = idx === currentCardIndex - 1;
                            const isVisible = isCurrent || isNext || isPrev;

                            if (!isVisible) return null;

                            // Styling stack offset coordinates
                            let zIndex = 10;
                            let yOffset = 0;
                            let scale = 1;
                            let opacity = 1;

                            if (isCurrent) {
                              zIndex = 30;
                              yOffset = 0;
                              scale = 1;
                              opacity = 1;
                            } else if (isNext) {
                              zIndex = 20;
                              yOffset = 24;
                              scale = 0.93;
                              opacity = 0.7;
                            } else if (isPrev) {
                              zIndex = 5;
                              yOffset = -24;
                              scale = 0.93;
                              opacity = 0;
                            }

                            return (
                              <motion.div
                                key={artifact.id}
                                style={{ zIndex }}
                                animate={{ 
                                  y: yOffset, 
                                  scale, 
                                  opacity 
                                }}
                                transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                                className="absolute w-full h-[320px] rounded-3xl bg-[#0b1023] border border-white/10 p-6 flex flex-col justify-between shadow-2xl hover:border-yellow-500/40 transition-colors"
                              >
                                <div className="space-y-4">
                                  {/* Badge & Stat */}
                                  <div className="flex justify-between items-start">
                                    <span className="px-2.5 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 text-[10px] font-bold uppercase tracking-wider">
                                      {artifact.preview.badge}
                                    </span>
                                    {artifact.preview.heroStat && (
                                      <div className="text-right">
                                        <span className="text-3xl font-light text-slate-100 font-sans tracking-tight leading-none block">
                                          {artifact.preview.heroStat}
                                        </span>
                                        <span className="text-[9px] text-slate-500 font-medium">
                                          {artifact.preview.secondaryStat}
                                        </span>
                                      </div>
                                    )}
                                  </div>

                                  {/* Title & ELI5 summary */}
                                  <div className="space-y-2">
                                    <h3 className="text-xl font-serif font-bold text-slate-200">
                                      {artifact.name}
                                    </h3>
                                    <p className="text-xs text-slate-400 leading-relaxed font-medium">
                                      {artifact.preview.shortDescription}
                                    </p>
                                  </div>
                                </div>

                                {/* Actions */}
                                <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                                  <button 
                                    onClick={() => handleQuickAction(artifact)}
                                    className="text-xs font-bold text-yellow-500 hover:text-yellow-400 flex items-center space-x-1.5 group"
                                  >
                                    <span>{artifact.preview.quickAction.label}</span>
                                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                                  </button>
                                  <span className="text-[10px] text-slate-500 font-bold">
                                    {idx + 1} of {mockArtifacts.length}
                                  </span>
                                </div>
                              </motion.div>
                            );
                          })}
                        </AnimatePresence>
                      </div>
                    ) : (
                      
                      /* ── RESPONSIVE GRID VIEW ── */
                      <div className="w-full grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 overflow-y-auto max-h-[420px] px-1 py-2 no-scrollbar">
                        {mockArtifacts.map((artifact) => (
                          <div 
                            key={artifact.id}
                            className="bg-[#0b1023] border border-white/10 rounded-2xl p-5 flex flex-col justify-between h-[210px] shadow-md hover:border-yellow-500/40 transition-colors"
                          >
                            <div className="space-y-3">
                              <div className="flex justify-between items-center">
                                <span className="px-2 py-0.5 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 text-[9px] font-bold uppercase tracking-wider">
                                  {artifact.preview.badge}
                                </span>
                                {artifact.preview.heroStat && (
                                  <span className="text-sm font-semibold text-slate-300">
                                    {artifact.preview.heroStat}
                                  </span>
                                )}
                              </div>
                              <h3 className="text-sm font-serif font-bold text-slate-200">
                                {artifact.name}
                              </h3>
                              <p className="text-[11px] text-slate-400 leading-normal line-clamp-3 font-medium">
                                {artifact.preview.shortDescription}
                              </p>
                            </div>

                            <button 
                              onClick={() => handleQuickAction(artifact)}
                              className="text-[11px] font-bold text-yellow-500 hover:text-yellow-400 flex items-center space-x-1 group pt-2"
                            >
                              <span>{artifact.preview.quickAction.label}</span>
                              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Wallet Navigation Controls */}
                  {deckLayout === 'stack' && (
                    <div className="flex justify-center items-center space-x-4 py-4 shrink-0">
                      <button 
                        onClick={() => setCurrentCardIndex((prev) => Math.max(prev - 1, 0))}
                        disabled={currentCardIndex === 0}
                        className="p-2.5 rounded-full bg-white/[0.03] border border-white/5 text-slate-400 hover:text-white disabled:opacity-30 disabled:pointer-events-none transition-colors"
                      >
                        <ChevronLeft className="w-5 h-5" />
                      </button>
                      <span className="text-xs font-bold text-slate-500 font-mono">
                        {currentCardIndex + 1} / {mockArtifacts.length}
                      </span>
                      <button 
                        onClick={() => setCurrentCardIndex((prev) => Math.min(prev + 1, mockArtifacts.length - 1))}
                        disabled={currentCardIndex === mockArtifacts.length - 1}
                        className="p-2.5 rounded-full bg-white/[0.03] border border-white/5 text-slate-400 hover:text-white disabled:opacity-30 disabled:pointer-events-none transition-colors"
                      >
                        <ChevronRight className="w-5 h-5" />
                      </button>
                    </div>
                  )}

                  {/* Skip to Workspace Banner */}
                  <div className="w-full flex justify-center pt-2 pb-4 shrink-0">
                    <button 
                      onClick={() => setViewState('workspace')}
                      className="px-6 py-2.5 rounded-2xl bg-white/[0.03] hover:bg-white/[0.05] border border-white/5 text-xs text-slate-300 font-bold transition-all"
                    >
                      Skip to full Chat & Policy Workspace
                    </button>
                  </div>
                </motion.div>
              )}

              {/* ── WORKFLOW STATE 3: SPLIT-SCREEN WORKSPACE ── */}
              {viewState === 'workspace' && (
                <motion.div 
                  key="workspace-view"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 flex space-x-6 h-full overflow-hidden"
                >
                  
                  {/* Left Column: Chat Area (60% width) */}
                  <div className="flex-[6] flex flex-col justify-between h-full bg-transparent overflow-hidden">
                    
                    {/* Chat Messages Stream */}
                    <div className="flex-1 overflow-y-auto pr-2 space-y-4 no-scrollbar">
                      {chatHistory.length === 0 ? (
                        // Empty Chat Guidance
                        <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
                          <div className="w-12 h-12 rounded-2xl bg-yellow-500/10 flex items-center justify-center text-yellow-500 border border-yellow-500/20">
                            <Bot className="w-6 h-6 animate-pulse" />
                          </div>
                          <div className="space-y-1">
                            <h3 className="text-sm font-bold text-slate-200">How can Mike help today?</h3>
                            <p className="text-xs text-slate-500 max-w-xs font-semibold">
                              Ask about procedure coverage, deductibles, waiting periods, or prescriptions.
                            </p>
                          </div>
                        </div>
                      ) : (
                        chatHistory.map((msg) => (
                          <div 
                            key={msg.id}
                            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} w-full`}
                          >
                            {msg.sender === 'user' ? (
                              <div className="px-4 py-3 rounded-2xl max-w-md bg-gradient-to-r from-yellow-500 to-amber-500 text-slate-950 font-medium text-xs shadow-md">
                                {msg.text}
                              </div>
                            ) : (
                              // Mike Bot Response UI Box
                              <div className="p-5 rounded-3xl max-w-xl bg-[#0b1023]/60 border border-white/5 text-xs text-slate-200 space-y-4 shadow-md w-full">
                                
                                {/* Header / Decision Badge */}
                                <div className="flex items-center justify-between">
                                  {msg.decision === 'likely_covered' && (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                      <CheckCircle2 className="w-3 h-3 mr-1" /> Likely Covered
                                    </span>
                                  )}
                                  {msg.decision === 'conditionally_covered' && (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-yellow-500/10 text-yellow-500 border border-yellow-500/20">
                                      <AlertCircle className="w-3 h-3 mr-1" /> Coverage Uncertain
                                    </span>
                                  )}
                                  {msg.decision === 'likely_not_covered' && (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                                      <X className="w-3 h-3 mr-1" /> Likely Not Covered
                                    </span>
                                  )}
                                  <span className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">
                                    Evidence Grounded
                                  </span>
                                </div>

                                {/* Short Plain-Text ELI5 Answer */}
                                <p className="font-bold text-slate-100 text-sm leading-snug">
                                  {msg.text}
                                </p>

                                {/* Detailed Medical/Insurance Reasoning */}
                                {msg.detailedReasoning && (
                                  <p className="text-[11px] leading-relaxed text-slate-400 font-medium">
                                    {msg.detailedReasoning}
                                  </p>
                                )}

                                {/* Conditions & Next Steps Lists */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                                  {msg.conditions && msg.conditions.length > 0 && (
                                    <div>
                                      <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Conditions</h5>
                                      <ul className="space-y-1.5 text-[11px] text-slate-400 font-semibold">
                                        {msg.conditions.map((cond, idx) => (
                                          <li key={idx} className="flex items-start">
                                            <ChevronRight className="w-3 h-3 mr-1 text-slate-500 shrink-0 mt-0.5" />
                                            <span>{cond}</span>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  
                                  {msg.nextSteps && msg.nextSteps.length > 0 && (
                                    <div>
                                      <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Next Steps</h5>
                                      <ul className="space-y-1.5 text-[11px] text-slate-400 font-semibold">
                                        {msg.nextSteps.map((step, idx) => (
                                          <li key={idx} className="flex items-start">
                                            <Check className="w-3 h-3 mr-1 text-yellow-500 shrink-0 mt-0.5" />
                                            <span>{step}</span>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>

                                {/* Source citations / Referenced Artifact links */}
                                {msg.referencedArtifactIds && msg.referencedArtifactIds.length > 0 && (
                                  <div className="pt-3 border-t border-white/5 space-y-2">
                                    <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                                      Verify Sources in Policy Workspace
                                    </h5>
                                    <div className="flex flex-wrap gap-2">
                                      {msg.referencedArtifactIds.map((artId) => {
                                        const originalArt = mockArtifacts.find(a => a.id === artId);
                                        if (!originalArt) return null;
                                        return (
                                          <button
                                            key={artId}
                                            onClick={() => handleCitationClick(artId)}
                                            className="px-2.5 py-1 rounded-lg bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-500 border border-yellow-500/20 transition-all font-bold text-[10px] flex items-center space-x-1"
                                          >
                                            <Bookmark className="w-3 h-3" />
                                            <span>{originalArt.name}</span>
                                          </button>
                                        );
                                      })}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        ))
                      )}

                      {/* Typing indicator */}
                      {isTyping && (
                        <div className="flex justify-start w-full">
                          <div className="px-4 py-3 rounded-2xl bg-[#0b1023]/60 border border-white/5 flex items-center space-x-1.5">
                            <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                        </div>
                      )}
                      
                      <div ref={messagesEndRef} />
                    </div>

                    {/* Bottom Action Area / Prompt Dock */}
                    <div className="pt-4 shrink-0 space-y-4">
                      
                      {/* Suggestion Chips */}
                      {showStarterChips && (
                        <div className="flex flex-wrap gap-2 justify-center">
                          <button 
                            onClick={() => triggerChatQuery('Summarize my insurance policy in simple terms.', [])}
                            className="px-3 py-1.5 rounded-full bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 text-[11px] font-bold text-slate-300 transition-all"
                          >
                            Summarize policy
                          </button>
                          <button 
                            onClick={() => triggerChatQuery('What medical services require prior authorization approvals?', [])}
                            className="px-3 py-1.5 rounded-full bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 text-[11px] font-bold text-slate-300 transition-all"
                          >
                            What requires prior-auth?
                          </button>
                          <button 
                            onClick={() => triggerChatQuery('Show me the major exclusions from this policy.', [])}
                            className="px-3 py-1.5 rounded-full bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 text-[11px] font-bold text-slate-300 transition-all"
                          >
                            List major exclusions
                          </button>
                        </div>
                      )}

                      {/* Chat Form Input */}
                      <form onSubmit={handleSendMessage} className="glass-input p-2 rounded-2xl flex items-center space-x-2">
                        <input 
                          type="text"
                          value={chatInput}
                          onChange={(e) => setChatInput(e.target.value)}
                          placeholder="Ask Mike about coverage rules..."
                          className="flex-1 bg-transparent px-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
                        />
                        <button 
                          type="submit"
                          className="p-2 rounded-xl bg-gradient-to-r from-yellow-500 to-amber-500 text-slate-950 font-bold hover:shadow-lg shadow-yellow-500/10 transition-all"
                        >
                          <Send className="w-3.5 h-3.5" />
                        </button>
                      </form>
                    </div>

                  </div>

                  {/* Right Column: Persistent Artifacts Panel (40% width) */}
                  <div className="flex-[4] flex flex-col h-full bg-[#0b1023]/40 border border-white/5 rounded-3xl overflow-hidden shadow-2xl relative">
                    
                    {/* Panel Header */}
                    <div className="p-4 border-b border-white/5 flex items-center justify-between shrink-0 bg-[#050816]/30">
                      <div className="flex items-center space-x-2">
                        <FileSpreadsheet className="w-4 h-4 text-yellow-500" />
                        <h3 className="font-serif font-bold text-sm text-slate-200">Policy Workspace</h3>
                      </div>
                      <span className="text-[10px] text-slate-500 font-bold">
                        {mockArtifacts.length} Artifacts
                      </span>
                    </div>

                    {/* Scrollable list of cards */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
                      {mockArtifacts.map((artifact) => {
                        const isOpen = activeArtifactId === artifact.id;
                        
                        return (
                          <div 
                            key={artifact.id}
                            ref={(el) => { artifactRefs.current[artifact.id] = el; }}
                            className={`border rounded-2xl overflow-hidden transition-all duration-300 ${
                              isOpen 
                                ? 'bg-[#0b1023]/90 border-yellow-500/30 shadow-lg' 
                                : 'bg-[#0b1023]/40 border-white/5 hover:border-white/10 hover:bg-[#0b1023]/60'
                            }`}
                          >
                            {/* Card Header toggle */}
                            <button
                              onClick={() => setActiveArtifactId(isOpen ? null : artifact.id)}
                              className="w-full flex items-center justify-between p-4 text-left focus:outline-none"
                            >
                              <div className="space-y-1">
                                <span className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                                  isOpen ? 'bg-yellow-500/10 text-yellow-500' : 'bg-white/5 text-slate-400'
                                }`}>
                                  {artifact.preview.badge}
                                </span>
                                <h4 className="font-serif font-bold text-sm text-slate-200 mt-1.5">
                                  {artifact.name}
                                </h4>
                              </div>
                              <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                            </button>

                            {/* Card Detail / Accordion Expansion view */}
                            {isOpen && (
                              <motion.div 
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                className="border-t border-white/5 p-4 space-y-4"
                              >
                                {/* Sections Accordion */}
                                <div className="space-y-2">
                                  {artifact.sections.map((sect) => {
                                    const isSectExpanded = expandedSections[`${artifact.id}_${sect.id}`] ?? false;
                                    
                                    // Highlight matching state (Soft Focus glow)
                                    const isHighlighted = highlightedReference?.artifactId === artifact.id && 
                                                          highlightedReference?.sectionId === sect.id;

                                    return (
                                      <div 
                                        key={sect.id}
                                        className={`border border-white/5 rounded-xl overflow-hidden transition-all ${
                                          isHighlighted ? 'animate-citation-pulse' : 'bg-[#050816]/30'
                                        }`}
                                      >
                                        <button
                                          onClick={() => setExpandedSections((prev) => ({
                                            ...prev,
                                            [`${artifact.id}_${sect.id}`]: !isSectExpanded
                                          }))}
                                          className="w-full flex items-center justify-between p-3 text-left focus:outline-none"
                                        >
                                          <span className="text-[11px] font-bold text-slate-300">
                                            {sect.title}
                                          </span>
                                          <ChevronDown className={`w-3.5 h-3.5 text-slate-500 transition-transform ${isSectExpanded ? 'rotate-180' : ''}`} />
                                        </button>

                                        {isSectExpanded && (
                                          <div className="p-3 border-t border-white/5 space-y-2 select-text">
                                            <p className="text-[11px] text-slate-400 leading-relaxed font-semibold">
                                              {sect.content}
                                            </p>
                                            
                                            {/* Source citations */}
                                            {sect.citations.map((cit, idx) => (
                                              <span 
                                                key={idx}
                                                className="inline-flex items-center text-[9px] font-bold text-yellow-500/70"
                                              >
                                                Source citation: {cit}
                                              </span>
                                            ))}
                                          </div>
                                        )}
                                      </div>
                                    );
                                  })}
                                </div>

                                {/* Deep CTAs (Level 2 Action Bar) */}
                                {artifact.deepCTAs && artifact.deepCTAs.length > 0 && (
                                  <div className="pt-2">
                                    {artifact.deepCTAs.map((action) => (
                                      <button
                                        key={action.id}
                                        onClick={() => handleDeepAction(action.payload, artifact.id)}
                                        className="w-full py-2 px-3 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 text-[11px] font-bold text-slate-300 text-left flex items-center justify-between group transition-all"
                                      >
                                        <span>{action.label}</span>
                                        <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-yellow-500 group-hover:translate-x-0.5 transition-all" />
                                      </button>
                                    ))}
                                  </div>
                                )}

                              </motion.div>
                            )}
                          </div>
                        );
                      })}
                    </div>

                  </div>
                </motion.div>
              )}

            </div>
          )}

        </AnimatePresence>
      </main>

    </div>
  );
}
