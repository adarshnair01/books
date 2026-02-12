import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Menu, X, Moon, Sun, Type,
  ChevronLeft, ChevronRight,
  ArrowUp, Bookmark, Search, Share2
} from 'lucide-react';

const App = () => {
  const [chapters, setChapters] = useState([]);
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [fontSize, setFontSize] = useState(parseInt(localStorage.getItem('fontSize')) || 22);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isUIVisible, setIsUIVisible] = useState(true);

  // Initial Load
  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}content/book.json`)
      .then(res => res.json())
      .then(data => {
        setChapters(data);
        setLoading(false);
      })
      .catch(err => console.error("Index load failed:", err));
  }, []);

  // Chapter Loader
  useEffect(() => {
    if (chapters.length > 0) {
      setLoading(true);
      fetch(`${import.meta.env.BASE_URL}content/${chapters[currentChapterIndex].filename}`)
        .then(res => res.text())
        .then(text => {
          setContent(text);
          setLoading(false);
          window.scrollTo({ top: 0, behavior: 'instant' });
        });
    }
  }, [currentChapterIndex, chapters]);

  // Scroll Tracking & UI Show/Hide
  useEffect(() => {
    let lastY = window.scrollY;
    const handleScroll = () => {
      const total = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / total) * 100;
      setScrollProgress(progress);

      if (window.scrollY > lastY + 20 && window.scrollY > 200) {
        setIsUIVisible(false);
      } else if (window.scrollY < lastY - 5) {
        setIsUIVisible(true);
      }
      lastY = window.scrollY;
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Theme Sync
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Persistent Font Size
  useEffect(() => {
    localStorage.setItem('fontSize', fontSize.toString());
  }, [fontSize]);

  if (loading && chapters.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-white dark:bg-[#050505]">
        <div className="font-sans text-[10px] uppercase tracking-[0.4em] opacity-30 animate-pulse font-bold">
          Assembling your library
        </div>
      </div>
    );
  }

  const currentChapter = chapters[currentChapterIndex];

  return (
    <div className="min-h-screen text-neutral-900 dark:text-neutral-100">

      {/* Top Professional Header */}
      <motion.header
        animate={{ y: isUIVisible ? 0 : -80, opacity: isUIVisible ? 1 : 0 }}
        className="fixed top-0 left-0 right-0 h-16 sm:h-20 z-40 flex items-center justify-between px-6 sm:px-10 bg-white/60 dark:bg-black/60 backdrop-blur-xl border-b border-neutral-100 dark:border-neutral-900/50"
      >
        <div className="flex items-center gap-6">
          <button onClick={() => setIsLibraryOpen(true)} className="action-btn">
            <Menu size={22} strokeWidth={1.5} />
          </button>
          <div className="h-6 w-[1px] bg-neutral-100 dark:bg-neutral-800 hidden sm:block" />
          <div className="hidden md:block">
            <h1 className="text-[9px] uppercase tracking-[0.3em] font-bold opacity-30 mb-0.5">Minimalist Guide</h1>
            <p className="font-serif italic text-sm">{currentChapter?.title}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className="action-btn">
            {theme === 'dark' ? <Sun size={20} strokeWidth={1.5} /> : <Moon size={20} strokeWidth={1.5} />}
          </button>
        </div>
      </motion.header>

      {/* Main Reading Flow */}
      <main className="reading-container">
        <AnimatePresence mode="wait">
          <motion.article
            key={currentChapterIndex}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
            className={`prose animate-reveal ${currentChapterIndex === 0 ? 'drop-cap' : ''}`}
            style={{ fontSize: `${fontSize}px` }}
          >
            <ReactMarkdown>{content}</ReactMarkdown>

            {/* Elegant Pagination Section */}
            <div className="mt-48 pt-24 border-t border-neutral-100 dark:border-neutral-900 flex flex-col items-center">
              <div className="flex items-center gap-16 sm:gap-24 mb-32">
                <button
                  disabled={currentChapterIndex === 0}
                  onClick={() => setCurrentChapterIndex(prev => prev - 1)}
                  className="group flex flex-col items-center gap-4 opacity-25 hover:opacity-100 transition-all disabled:opacity-5 cursor-pointer"
                >
                  <ChevronLeft size={48} strokeWidth={1} />
                  <span className="text-[10px] uppercase tracking-widest font-bold">Chapter {currentChapterIndex}</span>
                </button>

                <div className="text-center">
                  <span className="font-serif text-6xl italic opacity-5">{currentChapterIndex + 1}</span>
                </div>

                <button
                  disabled={currentChapterIndex === chapters.length - 1}
                  onClick={() => setCurrentChapterIndex(prev => prev + 1)}
                  className="group flex flex-col items-center gap-4 opacity-25 hover:opacity-100 transition-all disabled:opacity-5 cursor-pointer"
                >
                  <ChevronRight size={48} strokeWidth={1} />
                  <span className="text-[10px] uppercase tracking-widest font-bold">Chapter {currentChapterIndex + 2}</span>
                </button>
              </div>
              <div className="text-[9px] uppercase tracking-[0.5em] font-bold opacity-20">End of Text</div>
            </div>
          </motion.article>
        </AnimatePresence>
      </main>

      {/* Responsive Control Pod */}
      <motion.nav
        initial={{ y: 0 }}
        animate={{ y: isUIVisible ? 0 : 150 }}
        className="floating-bar"
      >
        <button onClick={() => setFontSize(s => Math.max(16, s - 2))} className="action-btn">
          <Type size={16} />
        </button>
        <div className="h-6 w-[1px] bg-neutral-200 dark:bg-neutral-800 mx-2" />
        <button onClick={() => setFontSize(s => Math.min(36, s + 2))} className="action-btn">
          <Type size={22} />
        </button>
        <div className="h-10 w-[1px] bg-neutral-200 dark:bg-neutral-800 mx-4" />
        <div className="flex flex-col items-start pr-6 py-1 min-w-[100px]">
          <div className="flex justify-between w-full text-[8px] uppercase tracking-widest font-bold opacity-30 mb-1">
            <span>Reading</span>
            <span>{Math.round(scrollProgress)}%</span>
          </div>
          <div className="w-full h-1 bg-neutral-100 dark:bg-neutral-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-black dark:bg-white"
              initial={false}
              animate={{ width: `${scrollProgress}%` }}
            />
          </div>
        </div>
      </motion.nav>

      {/* Library Sidebar (Drawer) */}
      <AnimatePresence>
        {isLibraryOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsLibraryOpen(false)}
              className="fixed inset-0 z-[100] bg-black/10 dark:bg-black/40 backdrop-blur-md"
            />
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 200 }}
              className="library-drawer"
            >
              <header className="flex justify-between items-center mb-16">
                <div>
                  <h2 className="text-[9px] uppercase tracking-[0.4em] font-bold opacity-30 mb-1">Library</h2>
                  <p className="font-serif italic text-3xl">GenAI Collection</p>
                </div>
                <button onClick={() => setIsLibraryOpen(false)} className="action-btn">
                  <X size={24} />
                </button>
              </header>

              <div className="flex-1 overflow-y-auto space-y-2 pr-4 scrollbar-hide">
                {chapters.map((ch, idx) => (
                  <div
                    key={ch.id}
                    onClick={() => {
                      setCurrentChapterIndex(idx);
                      setIsLibraryOpen(false);
                    }}
                    className={`toc-card group cursor-pointer ${idx === currentChapterIndex ? 'bg-neutral-50 dark:bg-neutral-900 px-4 -mx-4 rounded-xl' : 'hover:bg-neutral-50 dark:hover:bg-neutral-900/50 px-4 -mx-4 rounded-xl'}`}
                  >
                    <span className="font-sans text-[10px] font-bold opacity-20 pt-1.5 w-8">0{idx + 1}</span>
                    <div className="flex-1">
                      <h3 className={`font-serif text-xl sm:text-2xl leading-tight transition-all ${idx === currentChapterIndex ? 'italic font-bold' : 'opacity-70 group-hover:opacity-100'}`}>
                        {ch.title}
                      </h3>
                    </div>
                  </div>
                ))}
              </div>

              <footer className="mt-12 pt-8 border-t border-neutral-100 dark:border-neutral-900 flex justify-between items-center opacity-20 text-[9px] uppercase tracking-widest font-bold">
                <span>MMXXVI</span>
                <span>Archive v1.4</span>
              </footer>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Back to Top (Floating) */}
      {scrollProgress > 30 && isUIVisible && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 0.3, scale: 1 }}
          whileHover={{ opacity: 1 }}
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="fixed top-24 right-8 z-40 action-btn bg-white dark:bg-neutral-900 shadow-xl hidden lg:flex"
        >
          <ArrowUp size={20} />
        </motion.button>
      )}

    </div>
  );
};

export default App;
