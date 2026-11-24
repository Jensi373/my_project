
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "../../style/auth.css";

// Available restaurant themes
const themes = {
  terracotta: {
    themeName: "terracotta",
    primaryColor: "#c65d3a",
    secondaryColor: "#e7a66a",
    backgroundColor: "#faf7f2",
    cardColor: "#ffffff",
    textColor: "#292524",
  },

  ocean: {
    themeName: "ocean",
    primaryColor: "#176b87",
    secondaryColor: "#64ccc5",
    backgroundColor: "#f0f8fa",
    cardColor: "#ffffff",
    textColor: "#18323b",
  },

  forest: {
    themeName: "forest",
    primaryColor: "#28745b",
    secondaryColor: "#9bcb9a",
    backgroundColor: "#f2f8f1",
    cardColor: "#ffffff",
    textColor: "#25372a",
  },

  royal: {
    themeName: "royal",
    primaryColor: "#7041a6",
    secondaryColor: "#b99ae0",
    backgroundColor: "#f7f3fc",
    cardColor: "#ffffff",
    textColor: "#30263a",
  },

  rose: {
    themeName: "rose",
    primaryColor: "#c05270",
    secondaryColor: "#e9a2b1",
    backgroundColor: "#fff4f6",
    cardColor: "#ffffff",
    textColor: "#3e2930",
  },

  dark: {
    themeName: "dark",
    primaryColor: "#e0a84b",
    secondaryColor: "#d9b77e",
    backgroundColor: "#20242b",
    cardColor: "#303640",
    textColor: "#ffffff",
  },
};

type ThemeName = keyof typeof themes;

const RestaurantRegister: React.FC = () => {
  const navigate = useNavigate();

  // Registration fields
  const [restaurantName, setRestaurantName] = useState("");
  const [ownerName, setOwnerName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [address, setAddress] = useState("");

  // Logo
  const [logo, setLogo] = useState("");
  const [logoName, setLogoName] = useState("");

  // Theme selection
  const [selectedTheme, setSelectedTheme] =
    useState<ThemeName>("terracotta");

  // CAPTCHA
  const [captchaNum1] = useState(
    () => Math.floor(Math.random() * 10) + 1
  );

  const [captchaNum2] = useState(
    () => Math.floor(Math.random() * 10) + 1
  );

  const [captchaAnswer, setCaptchaAnswer] = useState("");

  const [loading, setLoading] = useState(false);

  // Logo upload handler
  const handleLogoChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image file.");
      event.target.value = "";
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      alert("Logo size should not exceed 2MB.");
      event.target.value = "";
      return;
    }

    const reader = new FileReader();

    reader.onloadend = () => {
      if (typeof reader.result === "string") {
        setLogo(reader.result);
        setLogoName(file.name);
      }
    };

    reader.onerror = () => {
      alert("Unable to read the selected image.");
    };

    reader.readAsDataURL(file);
  };

  // Registration handler
  const handleRegister = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    // Empty field validation
    if (
      !restaurantName.trim() ||
      !ownerName.trim() ||
      !email.trim() ||
      !phone.trim() ||
      !password ||
      !confirmPassword ||
      !address.trim()
    ) {
      alert("Please fill in all required fields.");
      return;
    }

    // Password validation
    if (password.length < 6) {
      alert("Password must contain at least 6 characters.");
      return;
    }

    if (password !== confirmPassword) {
      alert("Password and Confirm Password do not match.");
      return;
    }

    // CAPTCHA validation
    if (Number(captchaAnswer) !== captchaNum1 + captchaNum2) {
      alert("Incorrect CAPTCHA answer.");
      return;
    }

    setLoading(true);

    try {
      const selectedThemeData = themes[selectedTheme];

      const registrationData = {
        restaurantName: restaurantName.trim(),
        ownerName: ownerName.trim(),
        email: email.trim(),
        phone: phone.trim(),
        password,
        confirmPassword,
        address: address.trim(),

        // Save uploaded logo
        logo: logo,

        // Save selected restaurant theme
        theme: {
          ...selectedThemeData,
          themeName: selectedTheme,
        },
      };

      const response = await axios.post(
        "http://127.0.0.1:8000/api/restaurants/register",
        registrationData
      );

      if (response.status === 200 || response.status === 201) {
        alert("Restaurant registered successfully!");

        navigate("/login");
      }
    } catch (error: any) {
      console.error("Registration error:", error);

      const errorMessage =
        error.response?.data?.detail ||
        "Registration failed. Please try again.";

      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card register-card">

        <h1>Restaurant Registration</h1>

        <p className="auth-subtitle">
          Create your restaurant account
        </p>

        <form onSubmit={handleRegister}>

          {/* Restaurant Name */}
          <div className="form-group">
            <label>Restaurant Name</label>

            <input
              type="text"
              placeholder="Enter restaurant name"
              value={restaurantName}
              onChange={(e) =>
                setRestaurantName(e.target.value)
              }
            />
          </div>

          {/* Owner Name */}
          <div className="form-group">
            <label>Owner Name</label>

            <input
              type="text"
              placeholder="Enter owner name"
              value={ownerName}
              onChange={(e) =>
                setOwnerName(e.target.value)
              }
            />
          </div>

          {/* Email */}
          <div className="form-group">
            <label>Email Address</label>

            <input
              type="email"
              placeholder="Enter email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {/* Phone */}
          <div className="form-group">
            <label>Phone Number</label>

            <input
              type="tel"
              placeholder="Enter phone number"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>

          {/* Address */}
          <div className="form-group">
            <label>Restaurant Address</label>

            <textarea
              placeholder="Enter restaurant address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              rows={3}
            />
          </div>

          {/* Password */}
          <div className="form-group">
            <label>Password</label>

            <input
              type="password"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {/* Confirm Password */}
          <div className="form-group">
            <label>Confirm Password</label>

            <input
              type="password"
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
            />
          </div>

          {/* Restaurant Logo */}
          <div className="form-group">
            <label>Restaurant Logo</label>

            <label
              htmlFor="restaurantLogo"
              className="upload-label"
            >
              Choose Logo
            </label>

            <input
              id="restaurantLogo"
              type="file"
              accept="image/*"
              onChange={handleLogoChange}
              style={{ display: "none" }}
            />

            {logo && (
              <div className="logo-preview">
                <img
                  src={logo}
                  alt="Restaurant Logo Preview"
                  style={{
                    width: "100px",
                    height: "100px",
                    objectFit: "contain",
                    marginTop: "10px",
                    borderRadius: "10px",
                  }}
                />

                <p>{logoName}</p>

                <button
                  type="button"
                  onClick={() => {
                    setLogo("");
                    setLogoName("");

                    const fileInput =
                      document.getElementById(
                        "restaurantLogo"
                      ) as HTMLInputElement;

                    if (fileInput) {
                      fileInput.value = "";
                    }
                  }}
                >
                  Remove Logo
                </button>
              </div>
            )}
          </div>

          {/* Theme Selection */}
          <div className="form-group">
            <label>Choose Dashboard Theme</label>

            <select
              value={selectedTheme}
              onChange={(e) =>
                setSelectedTheme(e.target.value as ThemeName)
              }
            >
              <option value="terracotta">
                Terracotta
              </option>

              <option value="ocean">
                Ocean Blue
              </option>

              <option value="forest">
                Forest Green
              </option>

              <option value="royal">
                Royal Purple
              </option>

              <option value="rose">
                Rose Pink
              </option>

              <option value="dark">
                Dark Theme
              </option>
            </select>

            <small>
              This theme will be applied to your restaurant
              dashboard after registration.
            </small>
          </div>

          {/* CAPTCHA */}
          <div className="form-group">
            <label>
              CAPTCHA: What is {captchaNum1} + {captchaNum2}?
            </label>

            <input
              type="number"
              placeholder="Enter answer"
              value={captchaAnswer}
              onChange={(e) =>
                setCaptchaAnswer(e.target.value)
              }
            />
          </div>

          {/* Register Button */}
          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >
            {loading ? "Registering..." : "Register"}
          </button>

        </form>

        <p className="auth-footer">
          Already have an account?{" "}
          <Link to="/login">Login here</Link>
        </p>

      </div>
    </div>
  );
};

export default RestaurantRegister;
