"use client";

import React, { useState, useRef, useEffect } from "react";
import { getComprehensiveResearch, parseUserQuery } from "@/services/api";

function page() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle sending message
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setError(null);

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      { type: "user", content: userMessage, timestamp: new Date() },
    ]);
    setIsLoading(true);

    try {
      // Parse the user query
      const parsed = parseUserQuery(userMessage);

      if (parsed.needsClarification) {
        // If we can't parse, ask for clarification
        setMessages((prev) => [
          ...prev,
          {
            type: "assistant",
            content:
              "I'd love to help! Please provide both the business type and location. For example: 'coffee shop in Mumbai' or 'pharmacy in Pune'",
            timestamp: new Date(),
            needsClarification: true,
          },
        ]);
        setIsLoading(false);
        return;
      }

      // Show typing indicator
      setMessages((prev) => [
        ...prev,
        {
          type: "typing",
          content: "Analyzing market data...",
          timestamp: new Date(),
        },
      ]);

      // Fetch data from FastAPI backend
      const data = await getComprehensiveResearch(
        parsed.businessType,
        parsed.location,
        {
          includeRawData: false,
          useCache: true,
        }
      );

      console.log("✅ API Response received:", data);
      console.log("📊 Response keys:", Object.keys(data));
      console.log("📊 Full response:", JSON.stringify(data, null, 2));

      // Remove typing indicator
      setMessages((prev) => prev.filter((msg) => msg.type !== "typing"));

      // Add AI response with data
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          content: `Here's a comprehensive analysis for **${parsed.businessType}** in **${parsed.location}**:`,
          timestamp: new Date(),
          data: data,
        },
      ]);
    } catch (err) {
      console.error("API Error:", err);
      setMessages((prev) => prev.filter((msg) => msg.type !== "typing"));
      setError(err.message);
      setMessages((prev) => [
        ...prev,
        {
          type: "error",
          content:
            err.message || "Failed to fetch research data. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle suggestion pill clicks
  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div className="h-screen bg-blue-50 flex overflow-hidden relative">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-400/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/3 right-1/4 w-80 h-80 bg-blue-400/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
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
          {messages.length === 0 ? (
            // Welcome Screen
            <div className="flex flex-col items-center justify-center h-full text-center space-y-8 max-w-3xl mx-auto px-8">
              {/* Hero Text */}
              <div className="space-y-4">
                <h2 className="text-5xl font-bold text-slate-900 tracking-tight">
                  Let's create something
                  <span className="block text-blue-600">extraordinary</span>
                </h2>
                <p className="text-lg text-slate-600 max-w-md leading-relaxed mx-auto">
                  Start a conversation and unlock the power of AI-driven
                  insights for your business
                </p>
              </div>

              {/* Suggestion Pills */}
              <div className="flex flex-wrap gap-3 justify-center max-w-2xl">
                <button className="px-4 py-2 flex gap-3 bg-white/80  hover:bg-white backdrop-blur-sm rounded-full text-md font-medium text-slate-700 hover:text-slate-900 border border-gray-300 hover:border-10/50 hover:border-gray-800 ">
                  <img className="h-6 w-6" src="bulb.png" alt="" />
                  Business Strategy
                </button>

                <button
                  onClick={() => handleSuggestionClick("pharmacy in Pune")}
                  className="px-4 py-2 bg-white/80 hover:bg-white backdrop-blur-sm rounded-full text-sm font-medium text-slate-700 hover:text-slate-900 border border-white/40 hover:border-slate-200 transition-all duration-300 hover:shadow-md"
                >
                  💊 Pharmacy in Pune
                </button>

                <button
                  onClick={() => handleSuggestionClick("bakery in Delhi")}
                  className="px-4 py-2 bg-white/80 hover:bg-white backdrop-blur-sm rounded-full text-sm font-medium text-slate-700 hover:text-slate-900 border border-white/40 hover:border-slate-200 transition-all duration-300 hover:shadow-md"
                >
                  🥐 Bakery in Delhi
                </button>
              </div>
            </div>
          ) : (
            // Chat Messages
            <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
              {messages.map((message, index) => (
                <div key={index}>
                  {message.type === "user" && (
                    <div className="flex justify-end">
                      <div className="bg-blue-600 text-white px-6 py-3 rounded-2xl rounded-tr-sm max-w-2xl shadow-md">
                        <p className="text-sm">{message.content}</p>
                      </div>
                    </div>
                  )}

                  {message.type === "assistant" && (
                    <div className="flex justify-start">
                      <div className="space-y-4 max-w-3xl">
                        <div className="bg-white/90 backdrop-blur-sm px-6 py-4 rounded-2xl rounded-tl-sm shadow-md border border-white/40">
                          <p className="text-sm text-slate-800">
                            {message.content}
                          </p>
                        </div>

                        {/* Display Research Data */}
                        {message.data && (
                          <div className="space-y-4">
                            {/* Executive Summary */}
                            {message.data.executive_summary && (
                              <div className="bg-white/90 backdrop-blur-sm p-6 rounded-2xl shadow-md border border-white/40">
                                <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                                  <span className="text-xl">📋</span> Executive
                                  Summary
                                </h3>
                                <p className="text-sm text-slate-700 leading-relaxed mb-3">
                                  {
                                    message.data.executive_summary
                                      .business_overview
                                  }
                                </p>
                                {message.data.executive_summary
                                  .market_opportunity && (
                                  <p className="text-sm text-slate-700 leading-relaxed">
                                    {
                                      message.data.executive_summary
                                        .market_opportunity
                                    }
                                  </p>
                                )}
                              </div>
                            )}

                            {/* Market Overview */}
                            {message.data.market_analysis?.market_overview && (
                              <div className="bg-white/90 backdrop-blur-sm p-6 rounded-2xl shadow-md border border-white/40">
                                <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                                  <span className="text-xl">📊</span> Market
                                  Overview
                                </h3>
                                <div className="text-sm text-slate-700 leading-relaxed">
                                  {typeof message.data.market_analysis
                                    .market_overview === "string" ? (
                                    <p>
                                      {
                                        message.data.market_analysis
                                          .market_overview
                                      }
                                    </p>
                                  ) : typeof message.data.market_analysis
                                      .market_overview === "object" ? (
                                    <div className="space-y-3">
                                      {message.data.market_analysis
                                        .market_overview.market_size && (
                                        <div className="bg-blue-50 rounded-lg p-3">
                                          <p className="text-xs font-medium text-slate-600 mb-1">
                                            Market Size
                                          </p>
                                          <p className="text-sm font-semibold text-slate-800">
                                            {typeof message.data.market_analysis
                                              .market_overview.market_size ===
                                            "string"
                                              ? message.data.market_analysis
                                                  .market_overview.market_size
                                              : JSON.stringify(
                                                  message.data.market_analysis
                                                    .market_overview.market_size
                                                )}
                                          </p>
                                        </div>
                                      )}
                                      {message.data.market_analysis
                                        .market_overview.growth_rate && (
                                        <div className="bg-blue-50 rounded-lg p-3">
                                          <p className="text-xs font-medium text-slate-600 mb-1">
                                            Growth Rate
                                          </p>
                                          <p className="text-sm font-semibold text-slate-800">
                                            {typeof message.data.market_analysis
                                              .market_overview.growth_rate ===
                                            "string"
                                              ? message.data.market_analysis
                                                  .market_overview.growth_rate
                                              : JSON.stringify(
                                                  message.data.market_analysis
                                                    .market_overview.growth_rate
                                                )}
                                          </p>
                                        </div>
                                      )}
                                      {message.data.market_analysis
                                        .market_overview.customer_segments && (
                                        <div className="bg-blue-50 rounded-lg p-3">
                                          <p className="text-xs font-medium text-slate-600 mb-2">
                                            Customer Segments
                                          </p>
                                          {Array.isArray(
                                            message.data.market_analysis
                                              .market_overview.customer_segments
                                          ) ? (
                                            <ul className="list-disc list-inside space-y-1">
                                              {message.data.market_analysis.market_overview.customer_segments.map(
                                                (segment, idx) => (
                                                  <li
                                                    key={idx}
                                                    className="text-sm text-slate-700"
                                                  >
                                                    {segment}
                                                  </li>
                                                )
                                              )}
                                            </ul>
                                          ) : (
                                            <p className="text-sm text-slate-700">
                                              {typeof message.data
                                                .market_analysis.market_overview
                                                .customer_segments === "string"
                                                ? message.data.market_analysis
                                                    .market_overview
                                                    .customer_segments
                                                : JSON.stringify(
                                                    message.data.market_analysis
                                                      .market_overview
                                                      .customer_segments
                                                  )}
                                            </p>
                                          )}
                                        </div>
                                      )}
                                      {message.data.market_analysis
                                        .market_overview.key_drivers && (
                                        <div className="bg-blue-50 rounded-lg p-3">
                                          <p className="text-xs font-medium text-slate-600 mb-2">
                                            Key Drivers
                                          </p>
                                          {Array.isArray(
                                            message.data.market_analysis
                                              .market_overview.key_drivers
                                          ) ? (
                                            <ul className="list-disc list-inside space-y-1">
                                              {message.data.market_analysis.market_overview.key_drivers.map(
                                                (driver, idx) => (
                                                  <li
                                                    key={idx}
                                                    className="text-sm text-slate-700"
                                                  >
                                                    {driver}
                                                  </li>
                                                )
                                              )}
                                            </ul>
                                          ) : (
                                            <p className="text-sm text-slate-700">
                                              {typeof message.data
                                                .market_analysis.market_overview
                                                .key_drivers === "string"
                                                ? message.data.market_analysis
                                                    .market_overview.key_drivers
                                                : JSON.stringify(
                                                    message.data.market_analysis
                                                      .market_overview
                                                      .key_drivers
                                                  )}
                                            </p>
                                          )}
                                        </div>
                                      )}
                                    </div>
                                  ) : (
                                    <p>Market overview data unavailable</p>
                                  )}
                                </div>
                              </div>
                            )}

                            {/* Competitor Analysis */}
                            {message.data.market_analysis
                              ?.competitive_landscape && (
                              <div className="bg-white/90 backdrop-blur-sm p-6 rounded-2xl shadow-md border border-white/40">
                                <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
                                  <span className="text-xl">🎯</span> Competitor
                                  Analysis
                                </h3>
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                  <div className="bg-blue-50 rounded-xl p-4">
                                    <p className="text-xs text-slate-600 mb-1">
                                      Total Competitors
                                    </p>
                                    <p className="text-2xl font-bold text-blue-600">
                                      {
                                        message.data.market_analysis
                                          .competitive_landscape
                                          .total_competitors
                                      }
                                    </p>
                                  </div>
                                  <div className="bg-blue-50 rounded-xl p-4">
                                    <p className="text-xs text-slate-600 mb-1">
                                      Average Rating
                                    </p>
                                    <p className="text-2xl font-bold text-blue-600">
                                      {message.data.market_analysis.competitive_landscape.average_rating?.toFixed(
                                        1
                                      )}{" "}
                                      ⭐
                                    </p>
                                  </div>
                                  <div className="bg-blue-50 rounded-xl p-4">
                                    <p className="text-xs text-slate-600 mb-1">
                                      Market Saturation
                                    </p>
                                    <p className="text-xl font-bold text-blue-600">
                                      {
                                        message.data.market_analysis
                                          .competitive_landscape
                                          .market_saturation
                                      }
                                    </p>
                                  </div>
                                  <div className="bg-blue-50 rounded-xl p-4">
                                    <p className="text-xs text-slate-600 mb-1">
                                      Data Source
                                    </p>
                                    <p className="text-xs font-medium text-blue-600">
                                      {
                                        message.data.market_analysis
                                          .competitive_landscape.data_source
                                      }
                                    </p>
                                  </div>
                                </div>

                                {/* Top Competitors */}
                                {message.data.market_analysis
                                  .competitive_landscape.top_competitors &&
                                  message.data.market_analysis
                                    .competitive_landscape.top_competitors
                                    .length > 0 && (
                                    <div className="space-y-2">
                                      <p className="text-sm font-medium text-slate-700 mb-2">
                                        Top Competitors:
                                      </p>
                                      {message.data.market_analysis.competitive_landscape.top_competitors
                                        .slice(0, 3)
                                        .map((comp, idx) => (
                                          <div
                                            key={idx}
                                            className="border border-slate-200 rounded-lg p-3 bg-white/50"
                                          >
                                            <p className="font-medium text-sm text-slate-800">
                                              {comp.name}
                                            </p>
                                            <p className="text-xs text-slate-600 mt-1">
                                              {comp.address}
                                            </p>
                                            <div className="flex gap-3 mt-2 text-xs">
                                              <span className="text-yellow-600">
                                                ⭐ {comp.rating}
                                              </span>
                                              <span className="text-slate-500">
                                                📝 {comp.reviews} reviews
                                              </span>
                                              {comp.price_level && (
                                                <span className="text-green-600">
                                                  💰 ${comp.price_level}
                                                </span>
                                              )}
                                            </div>
                                          </div>
                                        ))}
                                    </div>
                                  )}
                              </div>
                            )}

                            {/* Market Trends */}
                            {message.data.market_analysis?.market_trends && (
                              <div className="bg-white/90 backdrop-blur-sm p-6 rounded-2xl shadow-md border border-white/40">
                                <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                                  <span className="text-xl">📈</span> Market
                                  Trends
                                </h3>
                                <div className="space-y-3">
                                  <div className="flex items-center justify-between bg-blue-50 rounded-lg p-3">
                                    <span className="text-sm text-slate-700">
                                      Growth Momentum
                                    </span>
                                    <span className="text-sm font-semibold text-blue-600 uppercase">
                                      {
                                        message.data.market_analysis
                                          .market_trends.growth_momentum
                                      }
                                    </span>
                                  </div>
                                  <div className="flex items-center justify-between bg-blue-50 rounded-lg p-3">
                                    <span className="text-sm text-slate-700">
                                      Average Interest
                                    </span>
                                    <span className="text-sm font-semibold text-blue-600">
                                      {
                                        message.data.market_analysis
                                          .market_trends.average_interest
                                      }
                                      /100
                                    </span>
                                  </div>
                                  {message.data.market_analysis.market_trends
                                    .opportunity_trends &&
                                    message.data.market_analysis.market_trends
                                      .opportunity_trends.length > 0 && (
                                      <div className="mt-3">
                                        <p className="text-xs font-medium text-slate-600 mb-2">
                                          Opportunity Trends:
                                        </p>
                                        <div className="space-y-2">
                                          {message.data.market_analysis.market_trends.opportunity_trends
                                            .slice(0, 5)
                                            .map((trendObj, idx) => (
                                              <div
                                                key={idx}
                                                className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-3 border border-green-100"
                                              >
                                                <div className="flex items-start justify-between gap-2">
                                                  <p className="text-sm text-slate-800 font-medium flex-1">
                                                    {typeof trendObj ===
                                                    "string"
                                                      ? trendObj
                                                      : trendObj.trend ||
                                                        trendObj.name ||
                                                        "Trend"}
                                                  </p>
                                                  {trendObj.momentum && (
                                                    <span
                                                      className={`text-xs px-2 py-1 rounded-full ${
                                                        trendObj.momentum.toLowerCase() ===
                                                          "rising" ||
                                                        trendObj.momentum.toLowerCase() ===
                                                          "high"
                                                          ? "bg-green-100 text-green-700"
                                                          : trendObj.momentum.toLowerCase() ===
                                                              "stable" ||
                                                            trendObj.momentum.toLowerCase() ===
                                                              "moderate"
                                                          ? "bg-blue-100 text-blue-700"
                                                          : "bg-orange-100 text-orange-700"
                                                      }`}
                                                    >
                                                      {trendObj.momentum}
                                                    </span>
                                                  )}
                                                </div>
                                                {trendObj.opportunity_type && (
                                                  <p className="text-xs text-slate-600 mt-1">
                                                    Type:{" "}
                                                    {trendObj.opportunity_type}
                                                  </p>
                                                )}
                                              </div>
                                            ))}
                                        </div>
                                      </div>
                                    )}
                                </div>
                              </div>
                            )}

                            {/* Business Viability */}
                            {message.data.business_viability && (
                              <div className="bg-white/90 backdrop-blur-sm p-6 rounded-2xl shadow-md border border-white/40">
                                <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                                  <span className="text-xl">💡</span> Business
                                  Viability & Recommendations
                                </h3>

                                {message.data.business_viability
                                  .viability_score && (
                                  <div className="mb-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-4">
                                    <p className="text-xs text-slate-600 mb-1">
                                      Viability Score
                                    </p>
                                    <p className="text-3xl font-bold text-blue-600">
                                      {
                                        message.data.business_viability
                                          .viability_score
                                      }
                                      /100
                                    </p>
                                  </div>
                                )}

                                {message.data.business_viability
                                  .strategic_recommendations && (
                                  <div className="text-sm text-slate-700 leading-relaxed">
                                    <p className="font-medium mb-2">
                                      Strategic Recommendations:
                                    </p>
                                    <p className="whitespace-pre-line">
                                      {
                                        message.data.business_viability
                                          .strategic_recommendations
                                      }
                                    </p>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* SearchAPI Insights */}
                            {message.data.searchapi_insights && (
                              <div className="bg-gradient-to-r from-purple-50 to-blue-50 backdrop-blur-sm p-6 rounded-2xl shadow-md border border-purple-200/40">
                                <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                                  <span className="text-xl">🔍</span> Real-Time
                                  Insights
                                </h3>
                                <div className="space-y-2 text-sm">
                                  <p className="text-slate-700">
                                    <span className="font-medium">
                                      Competitor Analysis:
                                    </span>{" "}
                                    {
                                      message.data.searchapi_insights
                                        .competitor_analysis
                                    }
                                  </p>
                                  <p className="text-slate-700">
                                    <span className="font-medium">
                                      Trend Analysis:
                                    </span>{" "}
                                    {
                                      message.data.searchapi_insights
                                        .trend_analysis
                                    }
                                  </p>
                                  {message.data.searchapi_insights
                                    .emerging_opportunities &&
                                    message.data.searchapi_insights
                                      .emerging_opportunities.length > 0 && (
                                      <div className="mt-3">
                                        <p className="font-medium text-slate-700 mb-2">
                                          Emerging Opportunities:
                                        </p>
                                        <div className="flex flex-wrap gap-2">
                                          {message.data.searchapi_insights.emerging_opportunities.map(
                                            (opp, idx) => (
                                              <span
                                                key={idx}
                                                className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full"
                                              >
                                                {opp}
                                              </span>
                                            )
                                          )}
                                        </div>
                                      </div>
                                    )}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {message.type === "typing" && (
                    <div className="flex justify-start">
                      <div className="bg-white/90 backdrop-blur-sm px-6 py-4 rounded-2xl rounded-tl-sm shadow-md border border-white/40">
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1">
                            <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></span>
                            <span
                              className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"
                              style={{ animationDelay: "0.2s" }}
                            ></span>
                            <span
                              className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"
                              style={{ animationDelay: "0.4s" }}
                            ></span>
                          </div>
                          <span className="text-sm text-slate-600">
                            {message.content}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {message.type === "error" && (
                    <div className="flex justify-start">
                      <div className="bg-red-50 border border-red-200 px-6 py-4 rounded-2xl rounded-tl-sm max-w-2xl shadow-md">
                        <p className="text-sm text-red-700">
                          ❌ {message.content}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-white/60 backdrop-blur-xl border-t border-white/20 p-6">
          <div className="flex gap-4 max-w-4xl mx-auto">
            <div className="flex-1 relative group">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                placeholder="Ask me anything about your business... (e.g., 'coffee shop in Mumbai')"
                className="w-full px-6 py-4 bg-white/90 backdrop-blur-sm border border-white/40 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400/50 transition-all duration-300 shadow-sm hover:shadow-md text-slate-800 placeholder-slate-500 group-hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="group px-6 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 disabled:cursor-not-allowed text-white rounded-2xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-medium relative overflow-hidden"
            >
              <div className="relative z-10 flex items-center gap-2">
                {isLoading ? (
                  <>
                    <svg
                      className="animate-spin w-5 h-5"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    <span className="hidden sm:inline">Analyzing...</span>
                  </>
                ) : (
                  <>
                    <span className="hidden sm:inline">Send</span>
                    <svg
                      className="w-5 h-5 transition-transform group-hover:translate-x-0.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                      />
                    </svg>
                  </>
                )}
              </div>
              <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </button>
          </div>

          {/* Footer */}
          <div className="text-center mt-4">
            <p className="text-xs text-slate-500">
              Powered by AI • Real-time Market Data • Your Privacy Matters
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default page;
