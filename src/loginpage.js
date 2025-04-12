import React, { useState } from "react";
import axios from "axios";
const LoginPage = () => {
  const [activeTab, setActiveTab] = useState("login");

  return (
    <div className="flex h-screen">
      {/* Left Section - Login/Register Form */}
      <div className="w-1/2 flex justify-center items-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-lg w-96">
          {/* Logo & Name */}
          <div className="flex items-center mb-6">
            <span className="text-2xl font-bold text-gray-800">BankBuddy</span>
          </div>

          {/* Tab Buttons */}
          <div className="flex border-b mb-4">
            <button
              className={`flex-1 py-2 text-lg font-medium ${
                activeTab === "login" ? "border-b-2 border-black text-black" : "text-gray-500"
              }`}
              onClick={() => setActiveTab("login")}
            >
              Login
            </button>
            <button
              className={`flex-1 py-2 text-lg font-medium ${
                activeTab === "register" ? "border-b-2 border-black text-black" : "text-gray-500"
              }`}
              onClick={() => setActiveTab("register")}
            >
              Register
            </button>
          </div>

          {/* Form */}
          <form>
            <input
              type="text"
              placeholder="Username"
              className="w-full px-4 py-2 mb-3 border rounded-md"
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full px-4 py-2 mb-3 border rounded-md"
            />

            <button className="w-full bg-black text-white py-2 rounded-md">
              {activeTab === "login" ? "Login" : "Register"}
            </button>
          </form>
        </div>
      </div>

      {/* Right Section - Welcome Message */}
      <div className="w-1/2 bg-gray-900 flex flex-col justify-center items-center text-white">
        <h2 className="text-3xl font-bold mb-4">Welcome to BankBuddy</h2>
        <p className="text-center w-3/4">
          Your trusted partner in modern banking. Experience secure transactions, real-time fraud detection, and personalized financial insights.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
