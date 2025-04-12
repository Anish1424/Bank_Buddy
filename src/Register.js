import React, { useState } from "react";
import { auth, db, createUserWithEmailAndPassword, setDoc, doc } from "../firebaseConfig";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const Register = () => {
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    phone: "",
    accountType: "savings", // Default account type
    balance: 5000, // Default initial balance
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      // Create user in Firebase Auth
      const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
      const user = userCredential.user;

      // Store user data in Firestore
      await setDoc(doc(db, "users", user.uid), {
        fullName: formData.fullName,
        email: formData.email,
        phone: formData.phone,
        accountType: formData.accountType,
        balance: formData.balance,
        createdAt: new Date(),
      });

      toast.success("Registration Successful!");
      setFormData({ fullName: "", email: "", password: "", phone: "", accountType: "savings", balance: 5000 });
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
        <input type="text" name="fullName" placeholder="Full Name" value={formData.fullName} onChange={handleChange} required />
        <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
        <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
        <input type="text" name="phone" placeholder="Phone Number" value={formData.phone} onChange={handleChange} required />
        
        <select name="accountType" value={formData.accountType} onChange={handleChange}>
          <option value="savings">Savings</option>
          <option value="current">Current</option>
        </select>

        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default Register;
