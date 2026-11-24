
import { BrowserRouter, Routes, Route } from "react-router-dom";

import RestaurantOrders from "./pages/restaurant/RestaurantOrders";
import RestaurantLogin from "./pages/restaurant/RestaurantLogin";
import RestaurantRegister from "./pages/restaurant/RestaurantRegister";
import RestaurantDashboard from "./pages/restaurant/RestaurantDashboard";
import RestaurantMenu from "./pages/restaurant/RestaurantMenu";
import RestaurantTables from "./pages/restaurant/RestaurantTables";
import AIAnalytics from "./pages/restaurant/AIAnalytics";
// import Kitchen from "./pages/restaurant/Kitchen";
import Feedback from "./pages/restaurant/Feedback";
import RestaurantKitchen from "./pages/restaurant/RestaurantKitchen";

import {
  RestaurantThemeProvider,
} from "./theme/RestaurantThemeContext";

import "./style/RestaurantTheme.css";

function App() {
  return (
    <BrowserRouter>
      <RestaurantThemeProvider>
        <Routes>
          <Route path="/login" element={<RestaurantLogin />} />
          <Route path="/register" element={<RestaurantRegister />} />
          <Route path="/dashboard" element={<RestaurantDashboard />} />
          <Route path="/menu" element={<RestaurantMenu />} />
          <Route path="/orders" element={<RestaurantOrders />} />
          <Route path="/tables" element={<RestaurantTables />} />
          <Route path="/ai-analytics" element={<AIAnalytics />} />
          {/* <Route path="/kitchen" element={<Kitchen />} /> */}
          <Route path="/kitchen" element={<RestaurantKitchen />}
/>
          <Route path="/feedback" element={<Feedback />} />
        </Routes>
      </RestaurantThemeProvider>
    </BrowserRouter>
  );
}

export default App;
