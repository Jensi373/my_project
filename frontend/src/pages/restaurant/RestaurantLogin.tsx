// // // import { useState } from "react";
// // // import { useNavigate, Link } from "react-router-dom";
// // // import axios from "axios";
// // // import "../../style/auth.css";

// // // function RestaurantLogin() {
// // //   const navigate = useNavigate();

// // //   const [email, setEmail] = useState("");
// // //   const [password, setPassword] = useState("");

// // //   const [loading, setLoading] = useState(false);

// // //   const handleSubmit = async (e: React.FormEvent) => {
// // //     e.preventDefault();

// // //     if (!email || !password) {
// // //       alert("Please enter email and password");
// // //       return;
// // //     }

// // //     try {
// // //       setLoading(true);

// // //       const response = await axios.post(
// // //         "http://127.0.0.1:8000/api/restaurants/login",
// // //         {
// // //           email,
// // //           password,
// // //         }
// // //       );

// // //       const data = response.data;

// // //       // Store restaurant information
// // //       localStorage.setItem("restaurantId", data.restaurantId);
// // //       localStorage.setItem("restaurantName", data.restaurantName);
// // //       localStorage.setItem("restaurantEmail", data.email);

// // //       alert(data.message);

// // //       navigate("/dashboard");

// // //     } catch (error: any) {
// // //       if (error.response) {
// // //         alert(error.response.data.detail);
// // //       } else {
// // //         alert("Unable to connect to backend");
// // //       }
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   return (
// // //     <div className="auth-page">

// // //       <div className="auth-card login-card">

// // //         <div className="auth-header">
// // //           <h1>Restaurant Login</h1>
// // //           <p>Login to manage your restaurant</p>
// // //         </div>

// // //         <form onSubmit={handleSubmit}>

// // //           <div className="form-group">
// // //             <label>Email</label>

// // //             <input
// // //               type="email"
// // //               placeholder="Enter your email"
// // //               value={email}
// // //               onChange={(e) => setEmail(e.target.value)}
// // //             />
// // //           </div>

// // //           <div className="form-group">
// // //             <label>Password</label>

// // //             <input
// // //               type="password"
// // //               placeholder="Enter your password"
// // //               value={password}
// // //               onChange={(e) => setPassword(e.target.value)}
// // //             />
// // //           </div>

// // //           <button
// // //             type="submit"
// // //             className="auth-button"
// // //             disabled={loading}
// // //           >
// // //             {loading ? "Logging in..." : "Login"}
// // //           </button>

// // //         </form>

// // //         <div className="auth-footer">

// // //           <p>
// // //             Don't have an account?{" "}
// // //             <Link to="/register">Register Restaurant</Link>
// // //           </p>

// // //         </div>

// // //       </div>

// // //     </div>
// // //   );
// // // }

// // // export default RestaurantLogin;

// // import { useState } from "react";
// // import { useNavigate, Link } from "react-router-dom";
// // import axios from "axios";

// // import "../../style/auth.css";

// // function RestaurantLogin() {

// //   const navigate = useNavigate();

// //   const [email, setEmail] = useState("");
// //   const [password, setPassword] = useState("");

// //   const [loading, setLoading] = useState(false);

// //   const handleSubmit = async (
// //     e: React.FormEvent
// //   ) => {

// //     e.preventDefault();

// //     if (!email || !password) {
// //       alert("Please enter email and password");
// //       return;
// //     }

// //     try {

// //       setLoading(true);

// //       const response = await axios.post(
// //         "http://127.0.0.1:8000/api/restaurants/login",
// //         {
// //           email,
// //           password,
// //         }
// //       );

// //       const data = response.data;

// //       localStorage.setItem(
// //         "restaurantId",
// //         data.restaurantId
// //       );

// //       localStorage.setItem(
// //         "restaurantName",
// //         data.restaurantName
// //       );

// //       localStorage.setItem(
// //         "restaurantEmail",
// //         data.email
// //       );

// //       alert(data.message);

// //       navigate("/dashboard");

// //     } catch (error: any) {

// //       if (error.response) {
// //         alert(error.response.data.detail);
// //       } else {
// //         alert("Unable to connect to backend");
// //       }

// //     } finally {

// //       setLoading(false);

// //     }
// //   };

// //   return (
// //     <div className="auth-page">

// //       <div className="auth-card login-card">

// //         <div className="auth-header">

// //           <h1>
// //             Restaurant Login
// //           </h1>

// //           <p>
// //             Login to manage your restaurant
// //           </p>

// //         </div>

// //         <form onSubmit={handleSubmit}>

// //           <div className="form-group">

// //             <label>
// //               Email
// //             </label>

// //             <input
// //               type="email"
// //               placeholder="Enter your email"
// //               value={email}
// //               onChange={(e) =>
// //                 setEmail(e.target.value)
// //               }
// //             />

// //           </div>

// //           <div className="form-group">

// //             <label>
// //               Password
// //             </label>

// //             <input
// //               type="password"
// //               placeholder="Enter your password"
// //               value={password}
// //               onChange={(e) =>
// //                 setPassword(e.target.value)
// //               }
// //             />

// //           </div>

// //           <button
// //             type="submit"
// //             className="auth-button"
// //             disabled={loading}
// //           >
// //             {loading
// //               ? "Logging in..."
// //               : "Login"}
// //           </button>

// //         </form>

// //         <div className="auth-footer">

// //           <p>
// //             Don't have an account?{" "}

// //             <Link to="/register">
// //               Register Restaurant
// //             </Link>
// //           </p>

// //         </div>

// //       </div>

// //     </div>
// //   );
// // }

// // export default RestaurantLogin;

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";

import "../../style/auth.css";

function RestaurantLogin() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Check empty fields
    if (!email || !password) {
      alert("Please enter email and password");
      return;
    }

    try {
      setLoading(true);

      // Login API
      const response = await axios.post(
        "http://127.0.0.1:8000/api/restaurants/login",
        {
          email,
          password,
        }
      );

      const data = response.data;

      // Store JWT token
      localStorage.setItem(
        "token",
        data.access_token
      );

      // Store restaurant ID
      // This ID is used to load the correct
      // restaurant dashboard
      localStorage.setItem(
        "restaurantId",
        data.restaurant_id
      );

      // Store restaurant name
      localStorage.setItem(
        "restaurantName",
        data.restaurantName
      );

      // Store email
      localStorage.setItem(
        "restaurantEmail",
        email
      );

      alert(data.message);

      // Open common restaurant dashboard
      navigate("/dashboard");

    } catch (error: any) {

      if (error.response) {
        alert(
          error.response.data.detail ||
          "Invalid email or password"
        );
      } else {
        alert("Unable to connect to backend");
      }

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">

      <div className="auth-card login-card">

        {/* Header */}
        <div className="auth-header">

          <h1>
            Restaurant Login
          </h1>

          <p>
            Login to manage your restaurant
          </p>

        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>

          {/* Email */}
          <div className="form-group">

            <label>
              Email
            </label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
            />

          </div>

          {/* Password */}
          <div className="form-group">

            <label>
              Password
            </label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
            />

          </div>

          {/* Login Button */}
          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >
            {loading
              ? "Logging in..."
              : "Login"}
          </button>

        </form>

        {/* Footer */}
        <div className="auth-footer">

          <p>
            Don't have an account?{" "}

            <Link to="/register">
              Register Restaurant
            </Link>
          </p>

        </div>

      </div>

    </div>
  );
}

export default RestaurantLogin;

