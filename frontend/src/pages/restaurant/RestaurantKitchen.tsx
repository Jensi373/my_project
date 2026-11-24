
import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../../style/RestaurantKitchen.css";

const API = "http://127.0.0.1:8000";

interface KitchenItem {
  food_id: string;
  name: string;
  category: string;
  price: number;
  quantity: number;
  subtotal: number;
  customizations?: any[];
  special_instructions?: string;
}

interface KitchenOrder {
  _id: string;
  order_number: string;
  customer_name: string;
  delivery_type: string;
  table_number?: string;
  items: KitchenItem[];
  total_items: number;
  total_price: number;
  order_status: string;
  created_at: string;
}

function RestaurantKitchen() {
  const navigate = useNavigate();

  const restaurantId = localStorage.getItem("restaurantId");
  const restaurantName =
    localStorage.getItem("restaurantName") || "Restaurant";

  const [orders, setOrders] = useState<KitchenOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingOrder, setUpdatingOrder] = useState("");
  const [error, setError] = useState("");

  const fetchOrders = useCallback(async () => {
    if (!restaurantId) {
      navigate("/login");
      return;
    }

    try {
      const response = await axios.get(
        `${API}/api/restaurants/${restaurantId}/orders`
      );

      setOrders(response.data.orders || []);
      setError("");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        "Unable to load kitchen orders."
      );
    } finally {
      setLoading(false);
    }
  }, [restaurantId, navigate]);

  useEffect(() => {
    if (!restaurantId) {
      navigate("/login");
      return;
    }

    fetchOrders();

    const interval = setInterval(() => {
      fetchOrders();
    }, 10000);

    return () => clearInterval(interval);
  }, [fetchOrders, restaurantId, navigate]);

  const updateStatus = async (
    orderId: string,
    newStatus: string
  ) => {
    if (!restaurantId) return;

    try {
      setUpdatingOrder(orderId);

      await axios.put(
        `${API}/api/restaurants/${restaurantId}/orders/${orderId}/status`,
        { status: newStatus }
      );

      await fetchOrders();

    } catch (err: any) {
      alert(
        err.response?.data?.detail ||
        "Unable to update order status."
      );
    } finally {
      setUpdatingOrder("");
    }
  };

  const getElapsedTime = (date: string) => {
    if (!date) return "Time unavailable";

    const minutes = Math.max(
      0,
      Math.floor(
        (Date.now() - new Date(date).getTime()) / 60000
      )
    );

    if (minutes < 60) {
      return `${minutes} min ago`;
    }

    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    return `${hours}h ${remainingMinutes}m ago`;
  };

  const acceptedOrders = orders.filter(
    (order) => order.order_status === "Accepted"
  );

  const preparingOrders = orders.filter(
    (order) => order.order_status === "Preparing"
  );

  const readyOrders = orders.filter(
    (order) => order.order_status === "Ready"
  );

  const renderOrderCard = (order: KitchenOrder) => (
    <div className="kitchen-order-card" key={order._id}>
      <div className="kitchen-order-header">
        <div>
          <h3>{order.order_number || order._id.slice(-6)}</h3>
          <p>{order.customer_name}</p>
        </div>

        <span className={`kitchen-status ${order.order_status.toLowerCase()}`}>
          {order.order_status}
        </span>
      </div>

      <div className="kitchen-order-info">
        <span>
          {order.delivery_type?.replace("_", " ").toUpperCase()}
        </span>

        {order.table_number && (
          <span>Table: {order.table_number}</span>
        )}

        <span>{getElapsedTime(order.created_at)}</span>
      </div>

      <div className="kitchen-items">
        <h4>Food Items</h4>

        {order.items.map((item, index) => (
          <div className="kitchen-food-item" key={`${item.food_id}-${index}`}>
            <div>
              <strong>{item.name}</strong>
              <p>{item.category}</p>

              {item.customizations &&
                item.customizations.length > 0 && (
                  <div className="kitchen-customizations">
                    {item.customizations.map((custom: any, i: number) => (
                      <p key={i}>
                        {custom.name || custom.title || "Customization"}:
                        {" "}
                        {custom.value || custom.option || ""}
                      </p>
                    ))}
                  </div>
                )}

              {item.special_instructions && (
                <p className="kitchen-instructions">
                  Note: {item.special_instructions}
                </p>
              )}
            </div>

            <strong>× {item.quantity}</strong>
          </div>
        ))}
      </div>

      <div className="kitchen-order-footer">
        <strong>
          Total Items: {order.total_items}
        </strong>

        {order.order_status === "Accepted" && (
          <button
            disabled={updatingOrder === order._id}
            onClick={() => updateStatus(order._id, "Preparing")}
          >
            {updatingOrder === order._id
              ? "Updating..."
              : "Start Preparing"}
          </button>
        )}

        {order.order_status === "Preparing" && (
          <button
            disabled={updatingOrder === order._id}
            onClick={() => updateStatus(order._id, "Ready")}
          >
            {updatingOrder === order._id
              ? "Updating..."
              : "Mark as Ready"}
          </button>
        )}

        {order.order_status === "Ready" && (
          <span className="kitchen-ready-label">
            Food is Ready
          </span>
        )}
      </div>
    </div>
  );

  return (
    <div className="kitchen-page">
      <div className="kitchen-header">
        <div>
          <h1>Kitchen Management</h1>
          <p>{restaurantName} · Kitchen Dashboard</p>
        </div>

        <button
          className="kitchen-refresh"
          onClick={fetchOrders}
        >
          Refresh Orders
        </button>
      </div>

      <div className="kitchen-stats">
        <div className="kitchen-stat">
          <span>New Orders</span>
          <h2>{acceptedOrders.length}</h2>
        </div>

        <div className="kitchen-stat">
          <span>Preparing</span>
          <h2>{preparingOrders.length}</h2>
        </div>

        <div className="kitchen-stat">
          <span>Ready</span>
          <h2>{readyOrders.length}</h2>
        </div>

        <div className="kitchen-stat">
          <span>Total Kitchen Orders</span>
          <h2>
            {acceptedOrders.length +
              preparingOrders.length +
              readyOrders.length}
          </h2>
        </div>
      </div>

      {error && (
        <div className="kitchen-error">{error}</div>
      )}

      {loading ? (
        <div className="kitchen-empty">
          Loading kitchen orders...
        </div>
      ) : (
        <div className="kitchen-columns">
          <section className="kitchen-column">
            <div className="kitchen-column-heading">
              <h2>New Orders</h2>
              <span>{acceptedOrders.length}</span>
            </div>

            {acceptedOrders.length === 0 ? (
              <p className="kitchen-empty">
                No new orders
              </p>
            ) : (
              acceptedOrders.map(renderOrderCard)
            )}
          </section>

          <section className="kitchen-column">
            <div className="kitchen-column-heading">
              <h2>Preparing</h2>
              <span>{preparingOrders.length}</span>
            </div>

            {preparingOrders.length === 0 ? (
              <p className="kitchen-empty">
                No orders preparing
              </p>
            ) : (
              preparingOrders.map(renderOrderCard)
            )}
          </section>

          <section className="kitchen-column">
            <div className="kitchen-column-heading">
              <h2>Ready</h2>
              <span>{readyOrders.length}</span>
            </div>

            {readyOrders.length === 0 ? (
              <p className="kitchen-empty">
                No ready orders
              </p>
            ) : (
              readyOrders.map(renderOrderCard)
            )}
          </section>
        </div>
      )}
    </div>
  );
}

export default RestaurantKitchen;
