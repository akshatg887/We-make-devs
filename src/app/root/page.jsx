"use client";

import React, { useState } from "react";

function page() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen font-[poppins] bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50 flex overflow-hidden relative">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-400/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/3 right-1/4 w-80 h-80 bg-indigo-400/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "w-80" : "w-0"
        } transition-all duration-500 ease-out bg-white/70 backdrop-blur-xl border-r border-white/20 overflow-hidden relative z-10`}
      >
        <div className="p-6 border-b border-white/10">
          <h2 className="text-lg font-semibold text-slate-800 tracking-tight">
            Conversations
          </h2>
          <p className="text-xs text-slate-500 mt-1">Recent chats</p>
        </div>
        <div className="p-4 space-y-3">
          <div className="group p-4 rounded-xl bg-gradient-to-r from-blue-50/50 to-transparent hover:from-blue-100/60 hover:to-blue-50/20 transition-all duration-300 cursor-pointer border border-transparent hover:border-blue-200/40">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 opacity-60 group-hover:opacity-100 transition-opacity"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-700 truncate group-hover:text-slate-900 transition-colors">
                  Product Strategy Discussion
                </p>
                <p className="text-xs text-slate-500 mt-1">2 hours ago</p>
              </div>
            </div>
          </div>
          <div className="group p-4 rounded-xl hover:bg-slate-50/60 transition-all duration-300 cursor-pointer border border-transparent hover:border-slate-200/40">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-slate-400 rounded-full mt-2 opacity-40 group-hover:opacity-60 transition-opacity"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-700 truncate group-hover:text-slate-900 transition-colors">
                  Technical Architecture
                </p>
                <p className="text-xs text-slate-500 mt-1">Yesterday</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative z-10">
        {/* Header */}
        <div className="bg-white/60 backdrop-blur-xl border-b border-white/20 p-6 flex items-center gap-6">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="group p-3 rounded-xl bg-white/80 hover:bg-white transition-all duration-100 shadow-sm hover:shadow-md border border-white/40"
          >
            <svg
              className={`w-5 h-5 text-slate-700 transition-transform duration-100 ${
                sidebarOpen ? "" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
          <div className="flex items-center gap-4">
            {/* <div className="relative">
              <div className="w-12 h-12 bg-black rounded-3xl flex items-center justify-center shadow-lg">
                <img src="" alt="" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
            </div> */}
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                BizGenie AI
              </h1>
              <p className="text-sm text-slate-500 font-medium">
                Your intelligent business assistant
              </p>
            </div>
          </div>
        </div>
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto relative">
          <div className="flex flex-col items-center justify-center h-full text-center space-y-8 max-w-3xl mx-auto px-8">
            {/* Hero Text */}
            <div className="space-y-4">
              <h2 className="text-6xl font-bold text-slate-900 tracking-tight">
                Let's create something
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                  Extraordinary
                </span>
              </h2>
              <p className="text-lg text-slate-600 max-w-md leading-relaxed mx-auto">
                Start a conversation and unlock the power of AI-driven insights
                for your business
              </p>
            </div>

            {/* Suggestion Pills */}
            <div className="flex flex-wrap gap-3 justify-center max-w-2xl">
              <button className="px-4 py-2 flex gap-3 bg-white/80  hover:bg-white backdrop-blur-sm rounded-full text-md font-medium text-slate-700 hover:text-slate-900 border border-gray-300 hover:border-10/50 hover:border-gray-800 ">
                <img className="h-6 w-6" src="bulb.png" alt="" />
                Business Strategy
              </button>

              <button className="px-4 py-2 flex gap-3 bg-white/80 hover:bg-white backdrop-blur-sm rounded-full text-md font-medium text-slate-700 hover:text-slate-900 border border-gray-300 hover:border-10/50 hover:border-gray-800 ">
                <img className="h-6 w-6" src="analysis.png" alt="" />
                Market Analysis
              </button>

              <button className="px-4 py-2 flex gap-3 bg-white/80 hover:bg-white backdrop-blur-sm rounded-full text-md font-medium text-slate-700 hover:text-slate-900 border border-gray-300 hover:border-10/50 hover:border-gray-800 ">
                <img className="h-6 w-6" src="chart2.png" alt="" />
                Growth Opportunities
              </button>
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white/60 backdrop-blur-xl border-t border-white/20 p-6">
          <div className="flex gap-4 max-w-4xl mx-auto">
            <div className="flex-1 relative group">
              <input
                type="text"
                placeholder="Ask me anything about your business..."
                className="w-full px-6 py-4 bg-white/90 backdrop-blur-sm border border-white/40 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400/50 transition-all duration-300 shadow-sm hover:shadow-md text-slate-800 placeholder-slate-500 group-hover:bg-white"
              />
              <button className="absolute cursor-pointer right-4 top-1/2 -translate-y-1/2 text-slate-400">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  className="w-5 h-5"
                >
                  <path d="M14.8287 7.75737L9.1718 13.4142C8.78127 13.8047 8.78127 14.4379 9.1718 14.8284C9.56232 15.219 10.1955 15.219 10.586 14.8284L16.2429 9.17158C17.4144 8.00001 17.4144 6.10052 16.2429 4.92894C15.0713 3.75737 13.1718 3.75737 12.0002 4.92894L6.34337 10.5858C4.39075 12.5384 4.39075 15.7042 6.34337 17.6569C8.29599 19.6095 11.4618 19.6095 13.4144 17.6569L19.0713 12L20.4855 13.4142L14.8287 19.0711C12.095 21.8047 7.66283 21.8047 4.92916 19.0711C2.19549 16.3374 2.19549 11.9053 4.92916 9.17158L10.586 3.51473C12.5386 1.56211 15.7045 1.56211 17.6571 3.51473C19.6097 5.46735 19.6097 8.63317 17.6571 10.5858L12.0002 16.2427C10.8287 17.4142 8.92916 17.4142 7.75759 16.2427C6.58601 15.0711 6.58601 13.1716 7.75759 12L13.4144 6.34316L14.8287 7.75737Z"></path>
                </svg>
              </button>
            </div>
            <button className="group px-6 py-4 bg-black text-white rounded-2xl transition-all duration-300 shadow-lg hover:shadow-xl font-medium relative overflow-hidden">
              <div className="relative z-10 flex items-center gap-2">
                <span className="hidden  sm:inline">Send</span>
                <img className="h-5 w-5" src="send.png" alt="" />
              </div>
            </button>
          </div>

          {/* Footer */}
          <div className="text-center mt-4">
            <p className="text-xs text-slate-500">
              Powered by advanced AI • Always learning • Your privacy matters
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default page;
