
import { NavLink, useNavigate } from "react-router-dom";
import "../../style/RestaurantSidebar.css";

function RestaurantSidebar() {
  const navigate = useNavigate();

  const restaurantName =
    localStorage.getItem("restaurantName") || "Restaurant";

  const navigationItems = [
  { label: "Dashboard", path: "/dashboard", icon: "⌂", enabled: true },
  { label: "Menu Management", path: "/menu", icon: "▤", enabled: true },
  { label: "Orders", path: "/orders", icon: "▣", enabled: true },
  { label: "Kitchen", path: "/kitchen", icon: "♨", enabled: true },
  { label: "Table Monitoring", path: "/tables", icon: "▦", enabled: true },
  { label: "Customer Feedback", path: "/feedback", icon: "☆", enabled: true },
  { label: "AI Insights", path: "/ai-analytics", icon: "✧", enabled: true },
  { label: "Inventory Overview", path: "/inventory", icon: "▧", enabled: false },
  { label: "Restaurant Settings", path: "/settings", icon: "⚙", enabled: false },
];

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("restaurantId");
    localStorage.removeItem("restaurantName");
    navigate("/login");
  };

  return (
    <aside className="restaurant-sidebar">
      <div className="rs-brand">
        <div className="rs-brand-icon">🍽️</div>
        <div className="rs-brand-text">
          <h2>Food Management</h2>
          <span>RESTAURANT PANEL</span>
        </div>
      </div>

      <div className="rs-restaurant">
        <div className="rs-restaurant-avatar">
          {restaurantName.charAt(0).toUpperCase()}
        </div>
        <div className="rs-restaurant-info">
          <span>LOGGED IN AS</span>
          <strong title={restaurantName}>{restaurantName}</strong>
        </div>
        <span className="rs-online-dot" title="Logged in" />
      </div>

      <div className="rs-nav-heading">WORKSPACE</div>

      <nav className="rs-navigation">
        {navigationItems.map((item) =>
          item.enabled ? (
            <NavLink
              key={item.label}
              to={item.path}
              end={item.path === "/dashboard"}
              className={({ isActive }) =>
                `rs-nav-link ${isActive ? "active" : ""}`
              }
            >
              <span className="rs-nav-icon">{item.icon}</span>
              <span className="rs-nav-label">{item.label}</span>
              <span className="rs-active-indicator" />
            </NavLink>
          ) : (
            <div
              key={item.label}
              className="rs-nav-link rs-disabled"
              title="This feature is not available yet"
              aria-disabled="true"
            >
              <span className="rs-nav-icon">{item.icon}</span>
              <span className="rs-nav-label">{item.label}</span>
              <span className="rs-coming-soon">Soon</span>
            </div>
          )
        )}
      </nav>

      <div className="rs-sidebar-bottom">
        <div className="rs-help-card">
          <span className="rs-help-icon">✦</span>
          <div>
            <strong>Smart Food Court</strong>
            <p>Manage your restaurant efficiently.</p>
          </div>
        </div>

        <button className="rs-logout-btn" onClick={handleLogout}>
          <span className="rs-logout-icon">↪</span>
          <span className="rs-nav-label">Logout</span>
        </button>

        <div className="rs-version">FOOD MANAGEMENT ECOSYSTEM</div>
      </div>
    </aside>
  );
}

export default RestaurantSidebar;
