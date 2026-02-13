import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { Routes, Route, useParams, useNavigate, Navigate } from 'react-router-dom';
import {
  Menu, X, Moon, Sun, Type,
  ChevronLeft, ChevronRight,
  ArrowUp, Bookmark
} from 'lucide-react';

const Bookshelf = ({ books, theme, setTheme }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#fafafa] dark:bg-[#050505] transition-colors duration-700">
      <header className="h-32 flex items-center justify-between px-12 border-b border-neutral-100 dark:border-neutral-900/50">
        <div>
          <h1 className="text-[10px] uppercase tracking-[0.5em] font-bold opacity-30 mb-1">Collections</h1>
          <p className="font-serif italic text-4xl">Your Private Archive</p>
        </div>
        <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className="action-btn">
          {theme === 'dark' ? <Sun size={20} strokeWidth={1.5} /> : <Moon size={20} strokeWidth={1.5} />}
        </button>
      </header>

      <main className="max-w-7xl mx-auto py-24 px-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
        {books.map((book) => (
          <motion.div
            key={book.id}
            whileHover={{ y: -10 }}
            onClick={() => navigate(`/${book.id}`)}
            className="group relative h-[500px] bg-white dark:bg-neutral-900 border border-neutral-100 dark:border-neutral-800 rounded-3xl overflow-hidden shadow-sm hover:shadow-2xl transition-all duration-500 cursor-pointer flex flex-col justify-end p-10"
          >
            <div className="absolute top-0 left-0 w-full h-3/5 bg-neutral-50 dark:bg-neutral-800/50 flex items-center justify-center group-hover:bg-neutral-100 dark:group-hover:bg-neutral-800 transition-all duration-700 overflow-hidden">
              {book.cover ? (
                <img
                  src={`${import.meta.env.BASE_URL}${book.cover}`}
                  alt={book.title}
                  className="w-full h-full object-cover opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all duration-1000"
                />
              ) : (
                <Bookmark className="opacity-10 group-hover:opacity-30 group-hover:scale-110 transition-all duration-500" size={120} strokeWidth={0.5} />
              )}
            </div>
            <div className="z-10">
              <h2 className="font-serif text-3xl leading-tight mb-4 group-hover:italic transition-all">
                {book.title}
              </h2>
              <div className="flex items-center gap-4 opacity-30 text-[9px] uppercase tracking-[0.3em] font-bold group-hover:opacity-60 transition-opacity">
                <span>Volume I</span>
                <div className="w-8 h-[1px] bg-current" />
                <span>Begin Reading</span>
              </div>
            </div>
          </motion.div>
        ))}
        {books.length === 0 && (
          <div className="col-span-full py-32 text-center opacity-30 italic font-serif text-2xl">
            No manuscripts found in the archives.
          </div>
        )}
      </main>
    </div>
  );
};

const Reader = ({ theme, setTheme, fontSize, setFontSize }) => {
  const { bookId } = useParams();
  const navigate = useNavigate();
  const [chapters, setChapters] = useState([]);
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isUIVisible, setIsUIVisible] = useState(true);
  const [bookTitle, setBookTitle] = useState('');
  const [bookPath, setBookPath] = useState('');
  const [hasStartedReading, setHasStartedReading] = useState(false);

  // 1. Load Book Index
  useEffect(() => {
    setLoading(true);
    setHasStartedReading(false); // Reset when book changes
    fetch(`${import.meta.env.BASE_URL}content/books.json`)
      .then(res => res.json())
      .then(allBooks => {
        const book = allBooks.find(b => b.id === bookId);
        if (book) {
          setBookTitle(book.title);
          const path = book.path || book.id;
          setBookPath(path);
          return fetch(`${import.meta.env.BASE_URL}content/${path}/book.json`);
        }
        throw new Error("Book not found");
      })
      .then(res => res.json())
      .then(data => {
        setChapters(data);
        setCurrentChapterIndex(0);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        navigate('/');
      });
  }, [bookId]);

  // 2. Chapter Loader
  useEffect(() => {
    if (chapters.length > 0 && hasStartedReading && bookPath) {
      setLoading(true);
      fetch(`${import.meta.env.BASE_URL}content/${bookPath}/${chapters[currentChapterIndex].filename}`)
        .then(res => res.text())
        .then(text => {
          setContent(text);
          setLoading(false);
          window.scrollTo({ top: 0, behavior: 'instant' });
        })
        .catch(err => console.error("Chapter load failed:", err));
    }
  }, [currentChapterIndex, chapters, bookPath, hasStartedReading]);

  // Scroll Tracking
  useEffect(() => {
    if (!hasStartedReading) return;
    let lastY = window.scrollY;
    const handleScroll = () => {
      const total = document.documentElement.scrollHeight - window.innerHeight;
      const progress = total > 0 ? (window.scrollY / total) * 100 : 0;
      setScrollProgress(progress);
      if (window.scrollY > lastY + 20 && window.scrollY > 200) setIsUIVisible(false);
      else if (window.scrollY < lastY - 5) setIsUIVisible(true);
      lastY = window.scrollY;
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [hasStartedReading]);

  if (loading && chapters.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-white dark:bg-[#050505]">
        <div className="font-sans text-[10px] uppercase tracking-[0.4em] opacity-30 animate-pulse font-bold text-neutral-900 dark:text-white">
          Accessing Manuscript...
        </div>
      </div>
    );
  }

  // Cover View
  if (!hasStartedReading) {
    return (
      <div className="min-h-screen bg-[#fafafa] dark:bg-[#050505] flex flex-col items-center justify-center p-12 transition-colors duration-700">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "circOut" }}
          className="max-w-4xl w-full text-center"
        >
          <div className="mb-12 flex justify-center">
            <div className="w-16 h-[1px] bg-neutral-200 dark:bg-neutral-800" />
          </div>
          <h2 className="text-[10px] uppercase tracking-[0.6em] font-bold opacity-30 mb-8">Featured Manuscript</h2>
          <h1 className="font-serif text-6xl sm:text-8xl leading-none mb-12 dark:text-white tracking-tight">
            {bookTitle}
          </h1>
          <p className="font-serif italic text-xl sm:text-2xl opacity-40 mb-20 max-w-2xl mx-auto leading-relaxed">
            A comprehensive inquiry into the foundations and future of modern intelligence.
          </p>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setHasStartedReading(true)}
            className="group relative px-12 py-6 bg-black dark:bg-white text-white dark:text-black rounded-full overflow-hidden transition-all duration-500 hover:shadow-[0_20px_50px_rgba(0,0,0,0.1)] dark:hover:shadow-[0_20px_50px_rgba(255,255,255,0.05)]"
          >
            <span className="relative z-10 text-[11px] uppercase tracking-[0.4em] font-bold">Begin Reading</span>
            <div className="absolute inset-0 bg-neutral-800 dark:bg-neutral-200 translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
          </motion.button>

          <div className="mt-32 flex flex-col items-center gap-6 opacity-20">
            <div className="w-[1px] h-24 bg-current animate-bounce" />
            <span className="text-[8px] uppercase tracking-widest font-bold">Scroll to discover</span>
          </div>
        </motion.div>
      </div>
    );
  }

  const currentChapter = chapters[currentChapterIndex];

  return (
    <div className="min-h-screen bg-white dark:bg-[#050505] text-neutral-900 dark:text-neutral-100 transition-colors duration-700">
      <motion.header
        animate={{ y: isUIVisible ? 0 : -80, opacity: isUIVisible ? 1 : 0 }}
        className="fixed top-0 left-0 right-0 h-16 sm:h-20 z-[80] flex items-center justify-between px-6 sm:px-10 bg-white/60 dark:bg-black/80 backdrop-blur-xl border-b border-neutral-100 dark:border-neutral-900/50"
      >
        <div className="flex items-center gap-6">
          <button onClick={() => setIsLibraryOpen(true)} className="action-btn">
            <Menu size={22} strokeWidth={1.5} />
          </button>
          <div className="h-6 w-[1px] bg-neutral-100 dark:bg-neutral-800 hidden sm:block" />
          <div className="hidden md:block">
            <h1 className="text-[9px] uppercase tracking-[0.3em] font-bold opacity-30 mb-0.5">{bookTitle}</h1>
            <p className="font-serif italic text-sm">{currentChapter?.title}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className="action-btn">
            {theme === 'dark' ? <Sun size={20} strokeWidth={1.5} /> : <Moon size={20} strokeWidth={1.5} />}
          </button>
        </div>
      </motion.header>

      <main className="reading-container pt-32 sm:pt-48 pb-64">
        <AnimatePresence mode="wait">
          <motion.article
            key={`${bookId}-${currentChapterIndex}`}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.8, ease: "circOut" }}
            className={`prose animate-reveal ${currentChapterIndex === 0 ? 'drop-cap' : ''}`}
            style={{ fontSize: `${fontSize}px` }}
          >
            <ReactMarkdown
              components={{
                img: ({ node, ...props }) => {
                  const src = props.src.startsWith('/')
                    ? `${import.meta.env.BASE_URL}${props.src.slice(1)}`
                    : props.src;
                  return (
                    <img
                      {...props}
                      src={src}
                      className="rounded-2xl shadow-lg my-12 border border-neutral-100 dark:border-neutral-900"
                    />
                  );
                }
              }}
            >
              {content}
            </ReactMarkdown>

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
            </div>
          </motion.article>
        </AnimatePresence>
      </main>

      <motion.nav animate={{ y: isUIVisible ? 0 : 150 }} className="floating-bar">
        <button onClick={() => setFontSize(s => Math.max(16, s - 2))} className="action-btn"><Type size={16} /></button>
        <div className="h-6 w-[1px] bg-neutral-200 dark:bg-neutral-800 mx-2" />
        <button onClick={() => setFontSize(s => Math.min(36, s + 2))} className="action-btn"><Type size={22} /></button>
        <div className="h-10 w-[1px] bg-neutral-200 dark:bg-neutral-800 mx-4" />
        <div className="flex flex-col items-start pr-6 py-1 min-w-[100px]">
          <div className="flex justify-between w-full text-[8px] uppercase tracking-widest font-bold opacity-30 mb-1">
            <span>Progress</span><span>{Math.round(scrollProgress)}%</span>
          </div>
          <div className="w-full h-1 bg-neutral-100 dark:bg-neutral-800 rounded-full overflow-hidden">
            <motion.div className="h-full bg-black dark:bg-white" animate={{ width: `${scrollProgress}%` }} />
          </div>
        </div>
      </motion.nav>

      <AnimatePresence>
        {isLibraryOpen && (
          <>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setIsLibraryOpen(false)}
              className="fixed inset-0 z-[100] bg-black/10 dark:bg-black/60 backdrop-blur-md" />
            <motion.div initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}
              className="library-drawer z-[110]" transition={{ type: 'spring', damping: 30, stiffness: 200 }}>
              <header className="flex justify-between items-center mb-16">
                <div>
                  <h2 className="text-[9px] uppercase tracking-[0.4em] font-bold opacity-30 mb-1">Manuscript</h2>
                  <p className="font-serif italic text-3xl">{bookTitle}</p>
                </div>
                <button onClick={() => setIsLibraryOpen(false)} className="action-btn"><X size={24} /></button>
              </header>

              <div className="flex-1 overflow-y-auto space-y-2 pr-4 scrollbar-hide">
                {chapters.map((ch, idx) => (
                  <div key={ch.id} onClick={() => { setCurrentChapterIndex(idx); setIsLibraryOpen(false); }}
                    className={`toc-card group cursor-pointer ${idx === currentChapterIndex ? 'bg-neutral-50 dark:bg-neutral-900 px-4 -mx-4 rounded-xl' : 'hover:bg-neutral-50 dark:hover:bg-neutral-900/50 px-4 -mx-4 rounded-xl'}`}>
                    <span className="font-sans text-[10px] font-bold opacity-20 pt-1.5 w-8">0{idx + 1}</span>
                    <div className="flex-1">
                      <h3 className={`font-serif text-xl sm:text-2xl leading-tight transition-all ${idx === currentChapterIndex ? 'italic font-bold' : 'opacity-70 group-hover:opacity-100'}`}>
                        {ch.title}
                      </h3>
                    </div>
                  </div>
                ))}
              </div>

              <footer className="mt-12 pt-8 border-t border-neutral-100 dark:border-neutral-900">
                <button onClick={() => navigate('/')} className="w-full py-4 text-[10px] uppercase tracking-[0.4em] font-bold opacity-40 hover:opacity-100 hover:text-red-500 transition-all">
                  Exit to Library
                </button>
              </footer>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

const App = () => {
  const [books, setBooks] = useState([]);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [fontSize, setFontSize] = useState(parseInt(localStorage.getItem('fontSize')) || 22);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}content/books.json`)
      .then(res => res.json())
      .then(data => setBooks(data))
      .catch(err => console.error("Books load failed:", err));
  }, []);

  useEffect(() => {
    if (theme === 'dark') document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <Routes>
      <Route path="/" element={<Bookshelf books={books} theme={theme} setTheme={setTheme} />} />
      <Route path="/:bookId" element={<Reader theme={theme} setTheme={setTheme} fontSize={fontSize} setFontSize={setFontSize} />} />
    </Routes>
  );
};

export default App;
