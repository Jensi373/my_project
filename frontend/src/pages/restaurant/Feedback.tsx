
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import RestaurantSidebar from "../../pages/restaurant/RestaurantSidebar";
import "../../style/Feedback.css";

const API = "http://127.0.0.1:8000";

interface FeedbackItem {
  _id: string;
  order_id: string;
  order_number: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  restaurant_id: string;
  food_id: string;
  food_name: string;
  category: string;
  rating: number;
  comment: string;
  created_at: string;
}

interface FoodSummary {
  food_id: string;
  food_name: string;
  total_reviews: number;
  average_rating: number;
}

function Feedback() {
  const navigate = useNavigate();

  const restaurantId = localStorage.getItem("restaurantId");
  const restaurantName =
    localStorage.getItem("restaurantName") || "Restaurant";

  const [feedbacks, setFeedbacks] = useState<FeedbackItem[]>([]);
  const [foodSummary, setFoodSummary] = useState<FoodSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [ratingFilter, setRatingFilter] = useState("All");
  const [foodFilter, setFoodFilter] = useState("All");

  const fetchFeedback = useCallback(async () => {
    if (!restaurantId) {
      setError("Restaurant ID not found. Please log in again.");
      setLoading(false);
      return;
    }

    try {
      setError("");

      const [feedbackResponse, summaryResponse] = await Promise.all([
        axios.get(
          `${API}/api/feedback/restaurant/${restaurantId}`
        ),
        axios.get(
          `${API}/api/feedback/restaurant/${restaurantId}/food-summary`
        )
      ]);

      setFeedbacks(feedbackResponse.data.feedbacks || []);
      setFoodSummary(summaryResponse.data.food_summary || []);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to load customer feedback."
      );
    } finally {
      setLoading(false);
    }
  }, [restaurantId]);

  useEffect(() => {
    if (!restaurantId) {
      navigate("/login");
      return;
    }

    fetchFeedback();

    const interval = setInterval(fetchFeedback, 30000);

    return () => clearInterval(interval);
  }, [restaurantId, navigate, fetchFeedback]);

  const averageRating = feedbacks.length
    ? (
        feedbacks.reduce((sum, item) => sum + item.rating, 0) /
        feedbacks.length
      ).toFixed(1)
    : "0.0";

  const getRatingCount = (rating: number) =>
    feedbacks.filter((item) => item.rating === rating).length;

  const positiveReviews = feedbacks.filter(
    (item) => item.rating >= 4
  ).length;

  const filteredFeedbacks = useMemo(() => {
    return feedbacks.filter((item) => {
      const searchText = search.toLowerCase();

      const matchesSearch =
        (item.customer_name || "").toLowerCase().includes(searchText) ||
        (item.food_name || "").toLowerCase().includes(searchText) ||
        (item.comment || "").toLowerCase().includes(searchText) ||
        (item.order_number || "").toLowerCase().includes(searchText);

      const matchesRating =
        ratingFilter === "All" ||
        item.rating === Number(ratingFilter);

      const matchesFood =
        foodFilter === "All" || item.food_id === foodFilter;

      return matchesSearch && matchesRating && matchesFood;
    });
  }, [feedbacks, search, ratingFilter, foodFilter]);

  const formatDate = (date: string) => {
    if (!date) return "Date unavailable";

    return new Date(date).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short"
    });
  };

  const renderStars = (rating: number) => (
    <span className="feedback-stars" aria-label={`${rating} out of 5 stars`}>
      {"★".repeat(Math.max(0, Math.min(5, rating)))}
      <span className="feedback-empty-stars">
        {"★".repeat(5 - Math.max(0, Math.min(5, rating)))}
      </span>
    </span>
  );

  return (
    <>
      <RestaurantSidebar />

      <div className="restaurant-content-area">
        <main className="feedback-page">

          <header className="feedback-header">
            <div>
              <span className="feedback-eyebrow">
                CUSTOMER EXPERIENCE
              </span>
              <h1>Customer Feedback</h1>
              <p>Read reviews about {restaurantName} and your food items.</p>
            </div>

            <button
              className="feedback-refresh-btn"
              onClick={fetchFeedback}
              disabled={loading}
            >
              ↻ Refresh
            </button>
          </header>

          {error && (
            <div className="feedback-error">
              {error}
              <button onClick={fetchFeedback}>Try Again</button>
            </div>
          )}

          {loading ? (
            <div className="feedback-loading">
              <span>⏳</span>
              <p>Loading customer feedback...</p>
            </div>
          ) : (
            <>
              <section className="feedback-stats">
                <div className="feedback-stat-card rating-stat">
                  <div className="feedback-stat-icon">⭐</div>
                  <div>
                    <p>Average Rating</p>
                    <h2>{averageRating} / 5</h2>
                    {renderStars(Number(averageRating))}
                  </div>
                </div>

                <div className="feedback-stat-card">
                  <div className="feedback-stat-icon">💬</div>
                  <div>
                    <p>Total Reviews</p>
                    <h2>{feedbacks.length}</h2>
                    <span>Customer feedback received</span>
                  </div>
                </div>

                <div className="feedback-stat-card">
                  <div className="feedback-stat-icon">❤️</div>
                  <div>
                    <p>Positive Reviews</p>
                    <h2>{positiveReviews}</h2>
                    <span>Ratings of 4 and 5 stars</span>
                  </div>
                </div>

                <div className="feedback-stat-card">
                  <div className="feedback-stat-icon">🍽️</div>
                  <div>
                    <p>Reviewed Food Items</p>
                    <h2>{foodSummary.length}</h2>
                    <span>Different food items reviewed</span>
                  </div>
                </div>
              </section>

              <section className="feedback-content-grid">

                <div className="feedback-main-section">
                  <div className="feedback-section-heading">
                    <div>
                      <h2>Customer Reviews</h2>
                      <p>Individual ratings and comments for your food.</p>
                    </div>
                    <span>{filteredFeedbacks.length} reviews</span>
                  </div>

                  <div className="feedback-toolbar">
                    <input
                      type="text"
                      placeholder="Search customer, food or comment..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />

                    <select
                      value={ratingFilter}
                      onChange={(e) => setRatingFilter(e.target.value)}
                    >
                      <option value="All">All Ratings</option>
                      <option value="5">5 Stars</option>
                      <option value="4">4 Stars</option>
                      <option value="3">3 Stars</option>
                      <option value="2">2 Stars</option>
                      <option value="1">1 Star</option>
                    </select>

                    <select
                      value={foodFilter}
                      onChange={(e) => setFoodFilter(e.target.value)}
                    >
                      <option value="All">All Food Items</option>
                      {foodSummary.map((food) => (
                        <option key={food.food_id} value={food.food_id}>
                          {food.food_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="feedback-review-list">
                    {filteredFeedbacks.length === 0 ? (
                      <div className="feedback-empty">
                        <span>💬</span>
                        <h3>No Reviews Found</h3>
                        <p>
                          Customer reviews matching your filters will appear here.
                        </p>
                      </div>
                    ) : (
                      filteredFeedbacks.map((item) => (
                        <article
                          className="feedback-review-card"
                          key={item._id}
                        >
                          <div className="feedback-review-top">
                            <div className="feedback-customer">
                              <div className="feedback-avatar">
                                {(item.customer_name || "C")
                                  .charAt(0)
                                  .toUpperCase()}
                              </div>

                              <div>
                                <h3>{item.customer_name || "Customer"}</h3>
                                <p>{item.customer_email || "Email unavailable"}</p>
                              </div>
                            </div>

                            <div className="feedback-review-rating">
                              {renderStars(item.rating)}
                              <strong>{item.rating}.0</strong>
                            </div>
                          </div>

                          <div className="feedback-food-info">
                            <span>🍽️ {item.food_name || "Food item"}</span>
                            <span>{item.category || "Food"}</span>
                          </div>

                          <p className="feedback-comment">
                            {item.comment?.trim()
                              ? `"${item.comment}"`
                              : "Customer submitted a rating without a written comment."}
                          </p>

                          <div className="feedback-review-footer">
                            <span>Order: {item.order_number || item.order_id}</span>
                            <span>{formatDate(item.created_at)}</span>
                          </div>
                        </article>
                      ))
                    )}
                  </div>
                </div>

                <aside className="feedback-sidebar">
                  <section className="feedback-rating-breakdown">
                    <h2>Rating Breakdown</h2>
                    <p>Customer rating distribution</p>

                    {[5, 4, 3, 2, 1].map((rating) => {
                      const count = getRatingCount(rating);
                      const percentage = feedbacks.length
                        ? (count / feedbacks.length) * 100
                        : 0;

                      return (
                        <div className="feedback-breakdown-row" key={rating}>
                          <span>{rating} ★</span>
                          <div className="feedback-progress">
                            <div style={{ width: `${percentage}%` }} />
                          </div>
                          <strong>{count}</strong>
                        </div>
                      );
                    })}
                  </section>

                  <section className="feedback-food-summary">
                    <h2>Food-wise Ratings</h2>
                    <p>Ratings for individual menu items</p>

                    {foodSummary.length === 0 ? (
                      <div className="feedback-small-empty">
                        No food ratings yet.
                      </div>
                    ) : (
                      foodSummary.map((food) => (
                        <div
                          className="feedback-food-summary-item"
                          key={food.food_id}
                        >
                          <div>
                            <strong>{food.food_name}</strong>
                            <span>{food.total_reviews} review(s)</span>
                          </div>
                          <strong className="food-average-rating">
                            ⭐ {Number(food.average_rating).toFixed(1)}
                          </strong>
                        </div>
                      ))
                    )}
                  </section>
                </aside>

              </section>
            </>
          )}

          <footer className="feedback-footer">
            Feedback refreshes automatically every 30 seconds.
          </footer>
        </main>
      </div>
    </>
  );
}

export default Feedback;
