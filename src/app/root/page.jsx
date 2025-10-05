"use client";
import React, { useState, useRef, useEffect } from "react";
import {
  getComprehensiveResearch,
  parseUserQuery,
  uploadCSV,
  chatWithCSV,
} from "@/services/api";
import CSVChart from "@/components/CSVChart";

function page() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Model selection state
  const [selectedModel, setSelectedModel] = useState("research"); // 'research' or 'csv'
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);

  // CSV-related state
  const [attachedFile, setAttachedFile] = useState(null);
  const [csvSessionId, setCsvSessionId] = useState(null);
  const fileInputRef = useRef(null);

  // Collapsible sections state - tracking which sections are expanded for each message
  const [expandedSections, setExpandedSections] = useState({});

  // Toggle section expansion
  const toggleSection = (messageIndex, sectionName) => {
    setExpandedSections((prev) => ({
      ...prev,
      [`${messageIndex}-${sectionName}`]:
        !prev[`${messageIndex}-${sectionName}`],
    }));
  };

  // Format message content - remove markdown formatting and make it more readable
  const formatMessageContent = (content) => {
    if (!content) return "";

    // Ensure content is a string
    const contentStr = typeof content === "string" ? content : String(content);

    // Remove markdown code blocks and quotes
    let formatted = contentStr
      .replace(/```[\s\S]*?```/g, "") // Remove code blocks
      .replace(/`([^`]+)`/g, "$1") // Remove inline code
      .replace(/^["']|["']$/g, "") // Remove leading/trailing quotes
      .replace(/\\n/g, "\n") // Convert escaped newlines
      .replace(/\*\*/g, "") // Remove bold markers
      .replace(/\*/g, "") // Remove italic markers
      .trim();

    return formatted;
  };

  // Component to render formatted text content
  const FormattedMessage = ({ content }) => {
    const formatted = formatMessageContent(content);

    // Split into paragraphs and bullet points
    const lines = formatted.split("\n").filter((line) => line.trim());

    return (
      <div className="space-y-2">
        {lines.map((line, index) => {
          const trimmedLine = line.trim();

          // Check if it's a bullet point
          if (trimmedLine.match(/^[-•*]\s/)) {
            return (
              <div key={index} className="flex items-start gap-2 ml-2">
                <span className="text-blue-600 text-sm leading-relaxed">•</span>
                <span className="text-sm text-gray-800 flex-1 leading-relaxed">
                  {trimmedLine.replace(/^[-•*]\s/, "")}
                </span>
              </div>
            );
          }

          // Check if it's a numbered list
          if (trimmedLine.match(/^\d+\./)) {
            return (
              <div key={index} className="flex items-start gap-2 ml-2">
                <span className="text-blue-600 font-medium text-sm leading-relaxed">
                  {trimmedLine.match(/^\d+/)[0]}.
                </span>
                <span className="text-sm text-gray-800 flex-1 leading-relaxed">
                  {trimmedLine.replace(/^\d+\.\s*/, "")}
                </span>
              </div>
            );
          }

          // Check if it's a heading (contains : at the end or is short and bold-looking)
          if (
            trimmedLine.endsWith(":") ||
            (trimmedLine.length < 50 && index < lines.length - 1)
          ) {
            return (
              <p
                key={index}
                className="text-sm font-semibold text-gray-900 mt-3 first:mt-0"
              >
                {trimmedLine}
              </p>
            );
          }

          // Regular paragraph
          return (
            <p key={index} className="text-sm text-gray-800 leading-relaxed">
              {trimmedLine}
            </p>
          );
        })}
      </div>
    );
  };

  // Collapsible Section Component
  const CollapsibleSection = ({
    title,
    icon,
    children,
    messageIndex,
    sectionKey,
    defaultExpanded = false,
  }) => {
    const isExpanded =
      expandedSections[`${messageIndex}-${sectionKey}`] ?? defaultExpanded;

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <button
          onClick={() => toggleSection(messageIndex, sectionKey)}
          className="w-full px-5 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
            <span className="text-base">{icon}</span> {title}
          </h3>
          <svg
            className={`w-5 h-5 text-gray-500 transition-transform ${
              isExpanded ? "rotate-180" : ""
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>
        {isExpanded && (
          <div className="px-5 pb-4 border-t border-gray-100 mt-0">
            <div className="mt-3">{children}</div>
          </div>
        )}
      </div>
    );
  };

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle file attachment
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type === "text/csv" || file.name.endsWith(".csv")) {
        setAttachedFile(file);
        setError(null);
        // Auto-switch to CSV agent when a file is uploaded
        setSelectedModel("csv");
      } else {
        setError("Please select a CSV file");
        e.target.value = null;
      }
    }
  };

  // Remove attached file
  const removeAttachedFile = () => {
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = null;
    }
  };

  // Handle sending message
  const handleSendMessage = async () => {
    if ((!inputValue.trim() && !attachedFile) || isLoading) return;

    const userMessage = inputValue.trim() || "Analyze this CSV file";
    setInputValue("");
    setError(null);

    // Add user message to chat with model info
    setMessages((prev) => [
      ...prev,
      {
        type: "user",
        content: userMessage,
        timestamp: new Date(),
        hasAttachment: !!attachedFile,
        fileName: attachedFile?.name,
        model: selectedModel, // Track which model this message is for
      },
    ]);
    setIsLoading(true);

    try {
      // Route to appropriate model based on selection
      if (selectedModel === "csv") {
        // CSV Agent Flow
        if (attachedFile) {
          // CSV Upload Flow
          setMessages((prev) => [
            ...prev,
            {
              type: "typing",
              content: "Analyzing your CSV file...",
              timestamp: new Date(),
              model: "csv",
            },
          ]);

          const uploadResult = await uploadCSV(attachedFile);

          // Store session ID for follow-up questions
          setCsvSessionId(uploadResult.session_id);

          // Remove typing indicator
          setMessages((prev) => prev.filter((msg) => msg.type !== "typing"));

          // Add AI response with CSV analysis
          setMessages((prev) => [
            ...prev,
            {
              type: "assistant",
              content: `Here's the analysis of **${attachedFile.name}**:`,
              timestamp: new Date(),
              csvData: uploadResult,
              dataType: "csv",
              model: "csv",
            },
          ]);

          // Clear the attached file after successful upload
          removeAttachedFile();
        } else if (csvSessionId && userMessage) {
          // CSV Follow-up Chat Flow
          setMessages((prev) => [
            ...prev,
            {
              type: "typing",
              content: "Analyzing...",
              timestamp: new Date(),
              model: "csv",
            },
          ]);

          const chatResult = await chatWithCSV(csvSessionId, userMessage);

          // Remove typing indicator
          setMessages((prev) => prev.filter((msg) => msg.type !== "typing"));

          // Add AI response
          setMessages((prev) => [
            ...prev,
            {
              type: "assistant",
              content: chatResult.parsed?.answer || chatResult.response,
              timestamp: new Date(),
              csvChatData: chatResult.parsed,
              dataType: "csv-chat",
              model: "csv",
            },
          ]);
        } else {
          // No CSV uploaded yet
          setMessages((prev) => [
            ...prev,
            {
              type: "assistant",
              content:
                "Please upload a CSV file to use the CSV Agent. Click the attachment icon to upload your file.",
              timestamp: new Date(),
              model: "csv",
            },
          ]);
        }
      } else {
        // Research Agent Flow
        const parsed = parseUserQuery(userMessage);

        if (parsed.needsClarification) {
          setMessages((prev) => [
            ...prev,
            {
              type: "assistant",
              content:
                "I'd love to help! Please provide both the business type and location. For example: 'coffee shop in Mumbai' or 'pharmacy in Pune'.",
              timestamp: new Date(),
              needsClarification: true,
              model: "research",
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
            model: "research",
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
            model: "research",
          },
        ]);
      }
    } catch (err) {
      console.error("API Error:", err);
      setMessages((prev) => prev.filter((msg) => msg.type !== "typing"));
      setError(err.message);
      setMessages((prev) => [
        ...prev,
        {
          type: "error",
          content:
            err.message || "Failed to process request. Please try again.",
          timestamp: new Date(),
          model: selectedModel,
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
    <div className="h-screen bg-gray-50 flex overflow-hidden">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "w-72" : "w-0"
        } transition-all duration-300 bg-white border-r border-gray-200 overflow-hidden`}
      >
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-base font-semibold text-gray-900">
            Conversations
          </h2>
          <p className="text-xs text-gray-500 mt-1">Recent chats</p>
        </div>
        <div className="p-3 space-y-2">
          <div className="p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer border border-transparent hover:border-gray-200">
            <p className="text-sm font-medium text-gray-700 truncate">
              Market Research
            </p>
            <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
          </div>
          <div className="p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer border border-transparent hover:border-gray-200">
            <p className="text-sm font-medium text-gray-700 truncate">
              CSV Analysis
            </p>
            <p className="text-xs text-gray-500 mt-1">Yesterday</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg
              className="w-5 h-5 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">BizGenie AI</h1>
            <p className="text-sm text-gray-500">
              Your intelligent business assistant
            </p>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            // Welcome Screen
            <div className="flex flex-col items-center justify-center h-full text-center space-y-8 max-w-2xl mx-auto px-8">
              {/* Hero Text */}
              <div className="space-y-3">
                <h2 className="text-4xl font-bold text-gray-900">
                  Welcome to BizGenie
                </h2>
                <p className="text-base text-gray-600 max-w-lg mx-auto">
                  Get market insights and analyze data with AI-powered agents
                </p>
                {/* Current Model Indicator */}
                <div className="flex items-center justify-center gap-2 mt-6">
                  <span className="text-sm text-gray-500">Active:</span>
                  <span
                    className={`text-sm font-medium px-3 py-1 rounded-lg ${
                      selectedModel === "csv"
                        ? "bg-green-50 text-green-700 border border-green-200"
                        : "bg-blue-50 text-blue-700 border border-blue-200"
                    }`}
                  >
                    {selectedModel === "csv" ? "CSV Agent" : "Research Agent"}
                  </span>
                </div>
              </div>

              {/* Suggestion Pills */}
              <div className="flex flex-wrap gap-2 justify-center max-w-xl">
                <button
                  onClick={() => handleSuggestionClick("pharmacy in Pune")}
                  className="px-4 py-2 bg-white hover:bg-gray-50 rounded-lg text-sm font-medium text-gray-700 border border-gray-200 hover:border-gray-300 transition-colors"
                >
                  💊 Pharmacy in Pune
                </button>

                <button
                  onClick={() => handleSuggestionClick("bakery in Delhi")}
                  className="px-4 py-2 bg-white hover:bg-gray-50 rounded-lg text-sm font-medium text-gray-700 border border-gray-200 hover:border-gray-300 transition-colors"
                >
                  🥐 Bakery in Delhi
                </button>

                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 bg-white hover:bg-gray-50 rounded-lg text-sm font-medium text-gray-700 border border-gray-200 hover:border-gray-300 transition-colors"
                >
                  📊 Upload CSV
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
                      <div className="max-w-2xl">
                        {/* Model Badge */}
                        <div className="flex justify-end mb-1">
                          <span
                            className={`text-xs px-2 py-0.5 rounded ${
                              message.model === "csv"
                                ? "bg-green-50 text-green-700 border border-green-200"
                                : "bg-blue-50 text-blue-700 border border-blue-200"
                            }`}
                          >
                            {message.model === "csv"
                              ? "CSV Agent"
                              : "Research Agent"}
                          </span>
                        </div>
                        <div className="bg-blue-600 text-white px-5 py-3 rounded-lg shadow-sm">
                          <p className="text-sm">{message.content}</p>
                          {message.hasAttachment && message.fileName && (
                            <div className="mt-2 flex items-center gap-2 bg-blue-700/50 rounded px-3 py-2">
                              <svg
                                className="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                />
                              </svg>
                              <span className="text-xs">
                                {message.fileName}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {message.type === "assistant" && (
                    <div className="flex justify-start">
                      <div className="space-y-3 max-w-3xl w-full">
                        {/* Model Badge */}
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-xs px-2 py-0.5 rounded ${
                              message.model === "csv"
                                ? "bg-green-50 text-green-700 border border-green-200"
                                : "bg-blue-50 text-blue-700 border border-blue-200"
                            }`}
                          >
                            {message.model === "csv"
                              ? "CSV Agent"
                              : "Research Agent"}
                          </span>
                        </div>
                        <div className="bg-white px-5 py-4 rounded-lg shadow-sm border border-gray-200">
                          <FormattedMessage content={message.content} />
                        </div>

                        {/* Display Research Data */}
                        {message.data && (
                          <div className="space-y-2">
                            {/* Executive Summary */}
                            {message.data.executive_summary && (
                              <CollapsibleSection
                                title="Executive Summary"
                                icon="📋"
                                messageIndex={index}
                                sectionKey="executive_summary"
                                defaultExpanded={true}
                              >
                                <div className="space-y-3">
                                  <FormattedMessage
                                    content={
                                      message.data.executive_summary
                                        .business_overview
                                    }
                                  />
                                  {message.data.executive_summary
                                    .market_opportunity && (
                                    <FormattedMessage
                                      content={
                                        message.data.executive_summary
                                          .market_opportunity
                                      }
                                    />
                                  )}
                                </div>
                              </CollapsibleSection>
                            )}

                            {/* Market Overview */}
                            {message.data.market_analysis?.market_overview && (
                              <CollapsibleSection
                                title="Market Overview"
                                icon="📊"
                                messageIndex={index}
                                sectionKey="market_overview"
                                defaultExpanded={false}
                              >
                                <div className="text-sm text-gray-700 leading-relaxed">
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
                                    <div className="space-y-2">
                                      {message.data.market_analysis
                                        .market_overview.market_size && (
                                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                          <p className="text-xs font-medium text-gray-600 mb-1">
                                            Market Size
                                          </p>
                                          <p className="text-sm font-semibold text-gray-800">
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
                                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                          <p className="text-xs font-medium text-gray-600 mb-1">
                                            Growth Rate
                                          </p>
                                          <p className="text-sm font-semibold text-gray-800">
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
                                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                          <p className="text-xs font-medium text-gray-600 mb-2">
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
                                                    className="text-sm text-gray-700"
                                                  >
                                                    {segment}
                                                  </li>
                                                )
                                              )}
                                            </ul>
                                          ) : (
                                            <p className="text-sm text-gray-700">
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
                                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                          <p className="text-xs font-medium text-gray-600 mb-2">
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
                                                    className="text-sm text-gray-700"
                                                  >
                                                    {driver}
                                                  </li>
                                                )
                                              )}
                                            </ul>
                                          ) : (
                                            <p className="text-sm text-gray-700">
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
                              </CollapsibleSection>
                            )}

                            {/* Competitor Analysis */}
                            {message.data.market_analysis
                              ?.competitive_landscape && (
                              <CollapsibleSection
                                title="Competitor Analysis"
                                icon="🎯"
                                messageIndex={index}
                                sectionKey="competitor_analysis"
                                defaultExpanded={false}
                              >
                                <div className="grid grid-cols-2 gap-3">
                                  <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                    <p className="text-xs text-gray-600 mb-1">
                                      Total Competitors
                                    </p>
                                    <p className="text-xl font-bold text-gray-900">
                                      {
                                        message.data.market_analysis
                                          .competitive_landscape
                                          .total_competitors
                                      }
                                    </p>
                                  </div>
                                  <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                    <p className="text-xs text-gray-600 mb-1">
                                      Average Rating
                                    </p>
                                    <p className="text-xl font-bold text-gray-900">
                                      {message.data.market_analysis.competitive_landscape.average_rating?.toFixed(
                                        1
                                      )}{" "}
                                      ⭐
                                    </p>
                                  </div>
                                  <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                    <p className="text-xs text-gray-600 mb-1">
                                      Market Saturation
                                    </p>
                                    <p className="text-lg font-bold text-gray-900">
                                      {
                                        message.data.market_analysis
                                          .competitive_landscape
                                          .market_saturation
                                      }
                                    </p>
                                  </div>
                                  <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                    <p className="text-xs text-gray-600 mb-1">
                                      Data Source
                                    </p>
                                    <p className="text-xs font-medium text-gray-700">
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
                                    <div className="space-y-2 mt-4">
                                      <p className="text-sm font-medium text-gray-700 mb-2">
                                        Top Competitors:
                                      </p>
                                      {message.data.market_analysis.competitive_landscape.top_competitors
                                        .slice(0, 3)
                                        .map((comp, idx) => (
                                          <div
                                            key={idx}
                                            className="border border-gray-200 rounded-lg p-3 bg-white"
                                          >
                                            <p className="font-medium text-sm text-gray-800">
                                              {comp.name}
                                            </p>
                                            <p className="text-xs text-gray-600 mt-1">
                                              {comp.address}
                                            </p>
                                            <div className="flex gap-3 mt-2 text-xs">
                                              <span className="text-yellow-600">
                                                ⭐ {comp.rating}
                                              </span>
                                              <span className="text-gray-500">
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
                              </CollapsibleSection>
                            )}

                            {/* Market Trends */}
                            {message.data.market_analysis?.market_trends && (
                              <CollapsibleSection
                                title="Market Trends"
                                icon="📈"
                                messageIndex={index}
                                sectionKey="market_trends"
                                defaultExpanded={false}
                              >
                                <div className="space-y-2">
                                  <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3 border border-gray-100">
                                    <span className="text-sm text-gray-700">
                                      Growth Momentum
                                    </span>
                                    <span className="text-sm font-semibold text-gray-900 uppercase">
                                      {
                                        message.data.market_analysis
                                          .market_trends.growth_momentum
                                      }
                                    </span>
                                  </div>
                                  <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3 border border-gray-100">
                                    <span className="text-sm text-gray-700">
                                      Average Interest
                                    </span>
                                    <span className="text-sm font-semibold text-gray-900">
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
                                        <p className="text-xs font-medium text-gray-600 mb-2">
                                          Opportunity Trends:
                                        </p>
                                        <div className="space-y-2">
                                          {message.data.market_analysis.market_trends.opportunity_trends
                                            .slice(0, 5)
                                            .map((trendObj, idx) => (
                                              <div
                                                key={idx}
                                                className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg p-3 border border-gray-200"
                                              >
                                                <p className="text-sm text-gray-800 font-medium">
                                                  {typeof trendObj === "string"
                                                    ? trendObj
                                                    : trendObj.trend ||
                                                      trendObj.name ||
                                                      "Trend"}
                                                </p>
                                                {trendObj.opportunity_type && (
                                                  <p className="text-xs text-gray-600 mt-1">
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
                              </CollapsibleSection>
                            )}

                            {/* Business Viability */}
                            {message.data.business_viability && (
                              <CollapsibleSection
                                title="Business Viability & Recommendations"
                                icon="💡"
                                messageIndex={index}
                                sectionKey="business_viability"
                                defaultExpanded={false}
                              >
                                {message.data.business_viability
                                  .viability_score && (
                                  <div className="mb-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg p-4 border border-gray-100">
                                    <p className="text-xs text-gray-600 mb-1">
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
                                  <div className="text-sm text-gray-700 leading-relaxed">
                                    <p className="font-medium mb-2">
                                      Strategic Recommendations:
                                    </p>
                                    <FormattedMessage
                                      content={
                                        message.data.business_viability
                                          .strategic_recommendations
                                      }
                                    />
                                  </div>
                                )}
                              </CollapsibleSection>
                            )}

                            {/* SearchAPI Insights */}
                            {message.data.searchapi_insights && (
                              <CollapsibleSection
                                title="Real-Time Insights"
                                icon="🔍"
                                messageIndex={index}
                                sectionKey="searchapi_insights"
                                defaultExpanded={false}
                              >
                                <div className="space-y-2 text-sm">
                                  <p className="text-gray-700">
                                    <span className="font-medium">
                                      Competitor Analysis:
                                    </span>{" "}
                                    {
                                      message.data.searchapi_insights
                                        .competitor_analysis
                                    }
                                  </p>
                                  <p className="text-gray-700">
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
                                        <p className="font-medium text-gray-700 mb-2">
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
                              </CollapsibleSection>
                            )}
                          </div>
                        )}

                        {/* CSV Analysis Data */}
                        {message.csvData && message.dataType === "csv" && (
                          <div className="space-y-2">
                            {/* Insights */}
                            {message.csvData.insights &&
                              message.csvData.insights.length > 0 && (
                                <CollapsibleSection
                                  title="Key Insights"
                                  icon="💡"
                                  messageIndex={index}
                                  sectionKey="csv_insights"
                                  defaultExpanded={true}
                                >
                                  <ul className="space-y-2">
                                    {message.csvData.insights.map(
                                      (insight, idx) => (
                                        <li
                                          key={idx}
                                          className="text-sm text-gray-700 flex items-start gap-2"
                                        >
                                          <span className="text-blue-600 mt-1">
                                            •
                                          </span>
                                          <span>{insight}</span>
                                        </li>
                                      )
                                    )}
                                  </ul>
                                </CollapsibleSection>
                              )}

                            {/* Anomalies */}
                            {message.csvData.anomalies &&
                              message.csvData.anomalies.length > 0 && (
                                <CollapsibleSection
                                  title="Anomalies Detected"
                                  icon="⚠️"
                                  messageIndex={index}
                                  sectionKey="csv_anomalies"
                                  defaultExpanded={false}
                                >
                                  <ul className="space-y-2">
                                    {message.csvData.anomalies.map(
                                      (anomaly, idx) => (
                                        <li
                                          key={idx}
                                          className="text-sm text-gray-700 flex items-start gap-2"
                                        >
                                          <span className="text-orange-600 mt-1">
                                            ⚠
                                          </span>
                                          <span>{anomaly}</span>
                                        </li>
                                      )
                                    )}
                                  </ul>
                                </CollapsibleSection>
                              )}

                            {/* Interactive Charts with Recharts */}
                            {message.csvData.chart_data &&
                              message.csvData.chart_data.length > 0 && (
                                <CollapsibleSection
                                  title="Data Visualizations"
                                  icon="📊"
                                  messageIndex={index}
                                  sectionKey="csv_charts"
                                  defaultExpanded={false}
                                >
                                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                    {message.csvData.chart_data.map(
                                      (chartData, idx) => (
                                        <CSVChart
                                          key={idx}
                                          chartSpec={chartData}
                                          data={chartData.data}
                                        />
                                      )
                                    )}
                                  </div>
                                </CollapsibleSection>
                              )}

                            {/* Recommendations */}
                            {message.csvData.recommendations &&
                              message.csvData.recommendations.length > 0 && (
                                <CollapsibleSection
                                  title="Recommendations"
                                  icon="✅"
                                  messageIndex={index}
                                  sectionKey="csv_recommendations"
                                  defaultExpanded={false}
                                >
                                  <ul className="space-y-2">
                                    {message.csvData.recommendations.map(
                                      (rec, idx) => (
                                        <li
                                          key={idx}
                                          className="text-sm text-gray-700 flex items-start gap-2"
                                        >
                                          <span className="text-green-600 mt-1">
                                            ✓
                                          </span>
                                          <span>{rec}</span>
                                        </li>
                                      )
                                    )}
                                  </ul>
                                </CollapsibleSection>
                              )}
                          </div>
                        )}

                        {/* CSV Chat Follow-up Data */}
                        {message.csvChatData &&
                          message.dataType === "csv-chat" && (
                            <div className="space-y-3">
                              {message.csvChatData.followUp &&
                                message.csvChatData.followUp.length > 0 && (
                                  <div className="bg-blue-50/90 backdrop-blur-sm p-4 rounded-xl shadow-sm border border-blue-200/40">
                                    <p className="text-xs font-medium text-slate-600 mb-2">
                                      💬 You might also want to ask:
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                      {message.csvChatData.followUp.map(
                                        (question, idx) => (
                                          <button
                                            key={idx}
                                            onClick={() => {
                                              setInputValue(question);
                                              inputRef.current?.focus();
                                            }}
                                            className="text-xs bg-white hover:bg-blue-100 text-blue-700 px-3 py-1.5 rounded-full border border-blue-200 transition-colors"
                                          >
                                            {question}
                                          </button>
                                        )
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
          {/* Attached File Display */}
          {attachedFile && (
            <div className="max-w-4xl mx-auto mb-3">
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 rounded-lg p-2">
                    <svg
                      className="w-5 h-5 text-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-800">
                      {attachedFile.name}
                    </p>
                    <p className="text-xs text-slate-500">
                      {(attachedFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={removeAttachedFile}
                  className="text-slate-500 hover:text-red-600 transition-colors p-1 rounded-lg hover:bg-red-50"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          )}

          <div className="flex gap-3 max-w-4xl mx-auto">
            {/* Model Selector Dropdown */}
            <div className="relative">
              <button
                onClick={() => setModelDropdownOpen(!modelDropdownOpen)}
                disabled={isLoading}
                className={`px-3 py-3 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg transition-colors flex items-center gap-2 ${
                  isLoading ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                {selectedModel === "research" ? (
                  <svg
                    className="w-5 h-5 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                ) : (
                  <svg
                    className="w-5 h-5 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                )}
                <svg
                  className={`w-4 h-4 text-gray-600 transition-transform ${
                    modelDropdownOpen ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {modelDropdownOpen && (
                <div className="absolute bottom-full mb-2 left-0 w-64 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden z-50">
                  <div className="p-2">
                    <button
                      onClick={() => {
                        setSelectedModel("research");
                        setModelDropdownOpen(false);
                      }}
                      className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                        selectedModel === "research"
                          ? "bg-blue-50 text-blue-700"
                          : "hover:bg-gray-50 text-gray-700"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <svg
                          className="w-5 h-5 text-blue-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                          />
                        </svg>
                        <div>
                          <p className="text-sm font-semibold">
                            Research Agent
                          </p>
                          <p className="text-xs text-gray-500">
                            Market analysis
                          </p>
                        </div>
                        {selectedModel === "research" && (
                          <svg
                            className="w-5 h-5 ml-auto text-blue-600"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                      </div>
                    </button>
                    <button
                      onClick={() => {
                        setSelectedModel("csv");
                        setModelDropdownOpen(false);
                      }}
                      className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                        selectedModel === "csv"
                          ? "bg-green-50 text-green-700"
                          : "hover:bg-gray-50 text-gray-700"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <svg
                          className="w-5 h-5 text-green-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                        <div>
                          <p className="text-sm font-semibold">CSV Agent</p>
                          <p className="text-xs text-gray-500">
                            Data analysis & CSV insights
                          </p>
                        </div>
                        {selectedModel === "csv" && (
                          <svg
                            className="w-5 h-5 ml-auto text-green-600"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                      </div>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* File Upload Button */}
            <div className="relative">
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                className="hidden"
                id="csv-upload"
              />
              <label
                htmlFor="csv-upload"
                className={`cursor-pointer px-3 py-3 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg transition-colors flex items-center gap-2 ${
                  isLoading ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                <svg
                  className="w-5 h-5 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                  />
                </svg>
              </label>
            </div>

            <div className="flex-1">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                placeholder={
                  selectedModel === "csv"
                    ? attachedFile
                      ? "Add a message about your CSV file (optional)..."
                      : csvSessionId
                      ? "Ask a follow-up question about your CSV data..."
                      : "Upload a CSV file to start analysis..."
                    : "Ask me anything about your business (e.g., 'pharmacy in Pune')..."
                }
                className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-800 placeholder-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={isLoading || (!inputValue.trim() && !attachedFile)}
              className="px-5 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium"
            >
              {isLoading ? (
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
              ) : (
                <svg
                  className="w-5 h-5"
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
              )}
            </button>
          </div>

          {/* Footer */}
          <div className="text-center mt-3">
            <p className="text-xs text-gray-500">
              Powered by AI • Real-time Market Data
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default page;
