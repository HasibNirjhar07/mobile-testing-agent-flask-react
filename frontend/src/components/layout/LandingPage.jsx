import React, { useRef, useState } from 'react';
import { motion, useScroll, useTransform, useSpring, useMotionValue } from 'framer-motion';
import { Smartphone, Globe, ArrowRight, Play, Cpu, Zap, Shield, Terminal } from 'lucide-react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';

// Magnetic Button Component
const MagneticButton = ({ children, className, onClick }) => {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const handleMouseMove = (e) => {
    const { clientX, clientY } = e;
    const { left, top, width, height } = ref.current.getBoundingClientRect();
    const centerX = left + width / 2;
    const centerY = top + height / 2;
    x.set((clientX - centerX) * 0.3); // Magnetic strength
    y.set((clientY - centerY) * 0.3);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.button
      ref={ref}
      style={{ x, y }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      className={clsx("relative z-10", className)}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {children}
    </motion.button>
  );
};

const FeatureCard = ({ title, description, icon: Icon, to, color }) => {
  const [hovered, setHovered] = useState(false);

  return (
    <Link to={to} className="block relative group">
      <motion.div
        className={clsx(
          "h-[400px] rounded-3xl p-8 border border-white/10 bg-noir-800/50 backdrop-blur-sm overflow-hidden transition-colors duration-500 relative",
          hovered ? (color === 'blue' ? "border-electric-blue/50" : "border-electric-purple/50") : ""
        )}
        onHoverStart={() => setHovered(true)}
        onHoverEnd={() => setHovered(false)}
        whileHover={{ y: -10 }}
      >
        <div className="absolute inset-0 bg-noise opacity-[0.03]"></div>
        
        {/* Glow Effect */}
        <motion.div 
          className={clsx(
            "absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-500 bg-gradient-to-br",
            color === 'blue' ? "from-electric-blue to-transparent" : "from-electric-purple to-transparent"
          )}
        />

        <div className="relative z-10 flex flex-col h-full justify-between">
          <div>
            <div className={clsx(
              "w-16 h-16 rounded-2xl flex items-center justify-center mb-6 text-white border border-white/10",
              color === 'blue' ? "bg-electric-blue/20" : "bg-electric-purple/20"
            )}>
              <Icon size={32} />
            </div>
            <h3 className="text-3xl font-serif font-medium text-white mb-4">{title}</h3>
            <p className="text-zinc-400 font-sans leading-relaxed text-lg">{description}</p>
          </div>

          <div className="flex items-center gap-2 font-mono text-sm tracking-widest uppercase opacity-70 group-hover:opacity-100 transition-opacity">
            <span className={color === 'blue' ? "text-electric-blue" : "text-electric-purple"}>
              Initialize Agent
            </span>
            <ArrowRight size={16} />
          </div>
        </div>

        {/* Background Icon */}
        <Icon 
          size={200} 
          className="absolute -bottom-10 -right-10 opacity-5 group-hover:opacity-10 transition-opacity duration-500 rotate-12" 
        />
      </motion.div>
    </Link>
  );
};

const LandingPage = () => {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: containerRef });
  const y = useTransform(scrollYProgress, [0, 1], [0, -50]);

  return (
    <div ref={containerRef} className="min-h-screen bg-noir-900 text-white selection:bg-electric-purple/30">
      
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 px-8 py-6 flex justify-between items-center bg-transparent backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center border border-white/10">
            <Cpu size={20} className="text-white" />
          </div>
          <span className="font-mono text-sm tracking-widest uppercase">Agent_Zero</span>
        </div>
        <div className="hidden md:flex gap-8 font-mono text-sm text-zinc-400">
          <a href="#" className="hover:text-white transition-colors">DOCS_01</a>
          <a href="#" className="hover:text-white transition-colors">GITHUB_REPO</a>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 overflow-hidden pt-32 pb-20">
        {/* Background Gradients */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-electric-blue/20 rounded-full blur-[120px] opacity-20 animate-pulse-fast"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-electric-purple/10 rounded-full blur-[100px] opacity-30"></div>

        <motion.div 
          initial={{ opacity: 0, y: 100 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center z-10"
        >
          <div className="mb-6 font-mono text-electric-cyan text-sm tracking-[0.2em] uppercase">
            System Operational // v2.0
          </div>
          
          <h1 className="text-5xl md:text-7xl lg:text-9xl font-serif font-medium leading-none tracking-tight mb-8 mix-blend-screen">
            Quality<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-zinc-200 via-zinc-500 to-zinc-800">Assurance</span><br />
            Reimagined.
          </h1>

          <p className="max-w-2xl mx-auto text-xl text-zinc-400 mb-12 font-light leading-relaxed">
            Deploy autonomous AI agents to stress-test your applications.
            <br />
            Visual regression, combat testing, and deep crawling at scale.
          </p>

          <MagneticButton className="group flex items-center gap-3 px-8 py-4 bg-white text-black rounded-full font-bold tracking-wide hover:bg-zinc-200 transition-colors">
            <Play size={20} fill="currentColor" />
            <span>START TESTING</span>
          </MagneticButton>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div 
          style={{ y }}
          className="absolute bottom-12 flex flex-col items-center gap-2 font-mono text-xs text-zinc-600 uppercase tracking-widest hidden md:flex"
        >
          <span>Scroll to Interact</span>
          <div className="w-[1px] h-12 bg-gradient-to-b from-zinc-600 to-transparent"></div>
        </motion.div>
      </section>

      {/* Agents Selection Grid */}
      <section className="py-32 px-6 max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-8">
          <FeatureCard 
            title="Mobile Agent" 
            description="Autonomous Android exploration via ADB. Detects crashes, validates UI logic, and understands context via Gemini Vision."
            icon={Smartphone}
            to="/dashboard/mobile"
            color="purple"
          />
          <FeatureCard 
            title="Web Agent" 
            description="Headless Chromium crawler. Performs deep smoke testing, asset validation, and multi-page journey analysis."
            icon={Globe}
            to="/dashboard/web"
            color="blue"
          />
        </div>
      </section>

      {/* Stats / Terminal Section */}
      <section className="py-20 border-t border-white/5 bg-black/40">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-12 text-center">
          <div>
            <div className="text-5xl font-mono text-white mb-2 font-bold">0.2s</div>
            <div className="text-zinc-500 font-mono text-sm uppercase tracking-widest">Inference Time</div>
          </div>
          <div>
            <div className="text-5xl font-mono text-white mb-2 font-bold">100%</div>
            <div className="text-zinc-500 font-mono text-sm uppercase tracking-widest">Local Execution</div>
          </div>
          <div>
            <div className="text-5xl font-mono text-white mb-2 font-bold">24/7</div>
            <div className="text-zinc-500 font-mono text-sm uppercase tracking-widest">Availability</div>
          </div>
        </div>
      </section>

      <footer className="py-8 text-center text-zinc-700 font-mono text-xs uppercase tracking-widest border-t border-white/5">
        <p>Built by Advanced Agentic Coding Team • 2026</p>
      </footer>
    </div>
  );
};

export default LandingPage;
