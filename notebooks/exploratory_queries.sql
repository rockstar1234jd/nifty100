-- Sprint 1 exploratory queries for nifty100.db

SELECT COUNT(*) AS company_count FROM companies;

SELECT broad_sector, COUNT(*) AS companies
FROM sectors
GROUP BY broad_sector
ORDER BY companies DESC, broad_sector;

SELECT company_id, COUNT(*) AS years
FROM profitandloss
GROUP BY company_id
ORDER BY years DESC, company_id
LIMIT 10;

SELECT c.company_name, p.year, p.net_profit
FROM profitandloss p
JOIN companies c ON c.id = p.company_id
ORDER BY p.net_profit DESC
LIMIT 10;

SELECT company_id, AVG(close_price) AS avg_close_price
FROM stock_prices
GROUP BY company_id
ORDER BY avg_close_price DESC
LIMIT 10;

SELECT company_id, year, market_cap_crore, pe_ratio, pb_ratio
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;
