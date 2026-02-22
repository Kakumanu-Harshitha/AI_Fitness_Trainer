import React, { useState, useEffect, useRef } from 'react';
import { Mic, Send, X, MicOff, Loader2 } from 'lucide-react';

/**
 * VoiceModal - Reusable modal for voice commands and AI coach questions
 */
const VoiceModal = ({ visible, onClose, onSubmit }) => {
    const [question, setQuestion] = useState('');
    const [processing, setProcessing] = useState(false);
    const [response, setResponse] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const recognitionRef = useRef(null);

    // Initialize Web Speech API
    useEffect(() => {
        if (visible && (window.SpeechRecognition || window.webkitSpeechRecognition)) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = true;
            recognitionRef.current.lang = 'en-US';

            recognitionRef.current.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');
                setQuestion(transcript);
            };

            recognitionRef.current.onend = () => {
                setIsRecording(false);
            };

            recognitionRef.current.onerror = (event) => {
                console.error('[VoiceModal] Speech recognition error:', event.error);
                setIsRecording(false);
            };
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, [visible]);

    // Auto-submit when recording ends and we have a transcript
    useEffect(() => {
        if (!isRecording && question.trim().length > 0 && !processing) {
            const timer = setTimeout(() => {
                handleSubmit();
            }, 500);
            return () => clearTimeout(timer);
        }
    }, [isRecording]);

    const toggleRecording = () => {
        if (!recognitionRef.current) {
            alert('Speech recognition is not supported in your browser.');
            return;
        }

        if (isRecording) {
            recognitionRef.current.stop();
        } else {
            setQuestion('');
            setResponse('');
            try {
                recognitionRef.current.start();
                setIsRecording(true);
            } catch (err) {
                console.error('[VoiceModal] Failed to start recording:', err);
                setIsRecording(false);
            }
        }
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        if (!question.trim() || processing) return;

        setProcessing(true);
        try {
            const result = await onSubmit(question);
            setResponse(result);
            setQuestion('');
        } catch (error) {
            setResponse('Sorry, I couldn\'t process that. Please try again.');
        } finally {
            setProcessing(false);
        }
    };

    const handleClose = () => {
        setQuestion('');
        setResponse('');
        setProcessing(false);
        onClose();
    };

    if (!visible) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-end justify-center sm:items-center p-0 sm:p-4">
            {/* Backdrop */}
            <div 
                className="absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
                onClick={handleClose}
            />

            {/* Modal Content */}
            <div className="relative w-full max-w-lg bg-white dark:bg-zinc-900 border-t sm:border border-gray-200 dark:border-zinc-800 rounded-t-[32px] sm:rounded-[32px] p-6 pb-10 sm:pb-8 shadow-2xl animate-in slide-in-from-bottom duration-300 transition-colors duration-300">
                {/* Header */}
                <div className="flex items-center gap-4 mb-6">
                    <div className="w-12 h-12 rounded-2xl bg-primary/20 flex items-center justify-center">
                        <Mic size={24} className="text-primary" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-xl font-black text-gray-900 dark:text-white">AI Coach</h3>
                        <p className="text-xs text-gray-500 dark:text-zinc-400 font-bold uppercase tracking-wider">Ask me anything about your workout</p>
                    </div>
                    <button 
                        onClick={handleClose}
                        className="p-2 text-gray-400 dark:text-zinc-500 hover:text-gray-900 dark:hover:text-white transition-colors"
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Response Display */}
                {response && (
                    <div className="bg-primary/10 border border-primary/20 rounded-2xl p-4 mb-6 animate-in fade-in zoom-in duration-300">
                        <p className="text-sm text-gray-800 dark:text-zinc-200 leading-relaxed">{response}</p>
                    </div>
                )}

                {/* Input Area */}
                <form onSubmit={handleSubmit} className="flex items-center gap-3 mb-6">
                    <button
                        type="button"
                        onClick={toggleRecording}
                        disabled={processing}
                        className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 border ${
                            isRecording 
                                ? 'bg-primary border-primary animate-pulse scale-110' 
                                : 'bg-primary/10 border-primary/30 hover:bg-primary/20'
                        }`}
                    >
                        {isRecording ? (
                            <MicOff size={24} className="text-black" />
                        ) : (
                            <Mic size={24} className="text-primary" />
                        )}
                    </button>

                    <div className="flex-1 relative">
                        <textarea
                            className="w-full bg-gray-100 dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded-2xl px-4 py-3 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-zinc-600 focus:outline-none focus:border-primary/50 transition-colors resize-none h-[48px]"
                            placeholder={isRecording ? "Listening..." : "e.g., How's my form?"}
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSubmit();
                                }
                            }}
                            disabled={processing || isRecording}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={!question.trim() || processing || isRecording}
                        className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 ${
                            question.trim() && !isRecording && !processing
                                ? 'bg-primary text-black'
                                : 'bg-gray-200 dark:bg-zinc-800 text-gray-400 dark:text-zinc-600'
                        }`}
                    >
                        {processing ? (
                            <Loader2 size={20} className="animate-spin" />
                        ) : (
                            <Send size={20} />
                        )}
                    </button>
                </form>

                {/* Quick Prompts */}
                <div className="space-y-3">
                    <p className="text-[10px] font-extrabold text-gray-500 dark:text-zinc-500 uppercase tracking-widest">Quick questions:</p>
                    <div className="flex flex-wrap gap-2">
                        {['How\'s my form?', 'Am I fatigued?', 'Tips for squats'].map((prompt) => (
                            <button
                                key={prompt}
                                type="button"
                                onClick={() => setQuestion(prompt)}
                                disabled={processing}
                                className="bg-gray-100 dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded-xl py-2 px-4 text-xs font-bold text-gray-600 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-zinc-700 transition-all active:scale-95"
                            >
                                {prompt}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VoiceModal;
