import React, { useState } from 'react';
import { ClerkProvider, SignedIn, SignedOut, SignIn, SignUp, UserButton, useAuth, useUser } from "@clerk/clerk-react";

// 🌟 YOUR CLERK KEY
const clerkPubKey = "pk_test_ZGVjZW50LXBpcmFuaGEtMTQuY2xlcmsuYWNjb3VudHMuZGV2JA";

// --- CHAT INTERFACE (No changes, keeping your working chat) ---
function ChatInterface() {
  const { getToken } = useAuth();
  const { user } = useUser();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMsg = { role: 'user', content: input };
    setMessages([...messages, newMsg]);
    setInput("");
    setLoading(true);

    try {
      const token = await getToken();
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: input })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Error connecting to backend." }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex h-screen bg-[#0F1117] text-white font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-[#171A26] border-r border-gray-800 p-4 hidden md:flex flex-col">
        <div className="flex items-center gap-2 mb-8">
          <span className="text-2xl">⚡</span>
          <h1 className="font-bold text-lg">Genius Bot</h1>
        </div>
        <div className="flex-1">
          <div className="text-xs text-gray-500 font-bold uppercase mb-3">Chat History</div>
          <div className="text-sm text-gray-400 hover:bg-gray-800 p-2 rounded cursor-pointer truncate">
            Recent conversation...
          </div>
        </div>
        <div className="border-t border-gray-800 pt-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UserButton />
            <div className="flex flex-col">
              <span className="text-sm font-medium">{user.fullName || "User"}</span>
              <span className="text-xs text-gray-500">{user.primaryEmailAddress?.toString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 opacity-80">
              <h2 className="text-3xl font-bold text-white mb-2">Welcome, {user.firstName}!</h2>
              <p>I am Sherpuri's Genius Bot. How can I help?</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-2xl ${
                msg.role === 'user' 
                ? 'bg-[#FDE047] text-black font-medium rounded-br-none' 
                : 'bg-[#1F2937] text-gray-100 border border-gray-700 rounded-bl-none'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && <div className="ml-4 text-gray-500 text-sm animate-pulse">Thinking...</div>}
        </div>

        <div className="p-4 bg-[#171A26] border-t border-gray-800">
          <div className="max-w-4xl mx-auto flex gap-3">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type a message..."
              className="flex-1 bg-[#0F1117] border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-yellow-400 transition-colors"
            />
            <button 
              onClick={sendMessage}
              className="bg-[#FDE047] hover:bg-yellow-400 text-black font-bold py-2 px-6 rounded-xl transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- LOGIN SCREEN (Forced Centering & Dark Mode) ---
function LoginScreen() {
  return (
    // This Outer Div forces everything to the center of the screen
    <div className="min-h-screen w-full bg-[#0F1117] flex flex-col items-center justify-center p-4">
      
      {/* Header Section */}
      <div className="w-full max-w-md text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Sherpuri's Genius Bot</h1>
        <p className="text-gray-400 text-sm">Welcome back! Please sign in to continue</p>
      </div>
      
      {/* Clerk Login Box */}
      <div className="flex justify-center w-full">
        <SignIn 
          appearance={{
            layout: { socialButtonsPlacement: "top" },
            variables: {
              colorPrimary: "#FDE047",   // Yellow Button
              colorText: "white",        // White Text
              colorBackground: "#171A26", // Dark Blue Card Background
              colorInputBackground: "#1F2433", // Dark Input Field
              colorInputText: "white",
              colorTextSecondary: "#9CA3AF",
              borderRadius: "0.5rem"
            },
            elements: {
              rootBox: "w-full flex justify-center",
              card: "bg-[#171A26] shadow-xl border border-[#2E3245] w-full max-w-md",
              headerTitle: "hidden", // HIDES the old "Sign in to AI Creator..." text
              headerSubtitle: "hidden", // HIDES the old subtitle
              socialButtonsBlockButton: "bg-[#262A3B] border-gray-700 text-white hover:bg-[#2E3245]",
              socialButtonsBlockButtonText: "text-white font-medium",
              dividerLine: "bg-gray-700",
              dividerText: "text-gray-500",
              formButtonPrimary: "bg-[#FDE047] hover:bg-yellow-400 text-black font-bold py-3 normal-case",
              formFieldLabel: "text-gray-300",
              formFieldInput: "bg-[#1F2433] border-gray-700 text-white focus:border-yellow-400",
              footerActionLink: "text-[#FDE047] hover:text-yellow-300"
            }
          }}
        />
      </div>
      
      <div className="mt-8 text-center">
        <p className="text-xs text-gray-600">Secured by Clerk</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <SignedOut>
        <LoginScreen />
      </SignedOut>
      <SignedIn>
        <ChatInterface />
      </SignedIn>
    </ClerkProvider>
  );
}