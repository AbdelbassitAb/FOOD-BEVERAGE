-- 2.3.3 Customer experience
-- A) Product review impact (proxy: average rating BY category)

SELECT
  product_category,
  AVG(rating) AS avg_rating,
  COUNT(*) AS nb_reviews
FROM SILVER.PRODUCT_REVIEWS_CLEAN
GROUP BY product_category
ORDER BY avg_rating DESC;

-- B) Customer service influence (satisfaction BY issue type)

SELECT
  issue_category,
  AVG(customer_satisfaction) AS avg_satisfaction,
  COUNT(*) AS nb_interactions
FROM SILVER.CUSTOMER_SERVICE_INTERACTIONS_CLEAN
GROUP BY issue_category
ORDER BY avg_satisfaction ASC;
