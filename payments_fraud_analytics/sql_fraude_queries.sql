-- Query 1
SELECT transaction_id, user_id, merchant_id, amount_inr, payment_method
FROM transactions
WHERE status = 'captured'
ORDER BY amount_inr DESC, transaction_id
LIMIT 10;

-- Output 1
/** transaction_id	user_id	merchant_id	amount_inr	payment_method
"TXN100046"	"208"	"11"	"4999"	"Netbanking"
"TXN100051"	"216"	"17"	"4999"	"UPI"
"TXN100075"	"151"	"15"	"4999"	"UPI"
"TXN100158"	"213"	"12"	"4999"	"UPI"
"TXN100220"	"62"	"1"	"4999"	"Wallet"
"TXN100282"	"293"	"27"	"4999"	"UPI"
"TXN100351"	"186"	"36"	"4999"	"UPI"
"TXN100390"	"149"	"3"	"4999"	"Wallet"
"TXN100409"	"281"	"33"	"4999"	"UPI"
"TXN100441"	"105"	"22"	"4999"	"UPI" 
**/

-- Query 2
SELECT DISTINCT payment_method, status
FROM transactions
ORDER BY payment_method, status;

-- Output 2
/** payment_method	status
"Card"	"captured"
"Card"	"chargeback"
"Card"	"failed"
"Netbanking"	"captured"
"Netbanking"	"chargeback"
"Netbanking"	"failed"
"UPI"	"captured"
"UPI"	"chargeback"
"UPI"	"failed"
"Wallet"	"captured"
"Wallet"	"chargeback"
"Wallet"	"failed" 
**/

-- Query 3
SELECT merchant_id,
       COUNT(*) AS transaction_count,
       SUM(amount_inr) AS total_amount_inr
FROM transactions
GROUP BY merchant_id
HAVING COUNT(*) >= 15
ORDER BY transaction_count DESC, merchant_id;

-- Output 3
/** merchant_id	transaction_count	total_amount_inr
"16"	"20"	"11130"
"29"	"19"	"13081"
"37"	"19"	"12931"
"9"	"18"	"4982"
"3"	"17"	"8233"
"25"	"17"	"15533"
"30"	"17"	"7883"
"7"	"16"	"15934"
"8"	"16"	"7434"
"22"	"16"	"12534"
"27"	"16"	"13584"
"34"	"16"	"10034"
"36"	"16"	"12534"
"31"	"15"	"4835"
"40"	"15"	"8735" 
**/

-- Query 4
SELECT COUNT(*) AS chargeback_transactions,
       COUNT(DISTINCT user_id) AS unique_users_affected,
       SUM(amount_inr) AS total_chargeback_amount_inr
FROM transactions
WHERE status = 'chargeback';

-- Output 4
/** chargeback_transactions	unique_users_affected	total_chargeback_amount_inr
 "28"	"27"	"54472" 
 **/

-- Query 5
SELECT m.merchant_id,
       m.merchant_name,
       m.category,
       COUNT(t.transaction_id) AS chargeback_count,
       SUM(t.amount_inr) AS chargeback_amount_inr
FROM merchants AS m
INNER JOIN transactions AS t
    ON m.merchant_id = t.merchant_id
WHERE t.status = 'chargeback'
GROUP BY m.merchant_id, m.merchant_name, m.category
HAVING COUNT(t.transaction_id) >= 1
ORDER BY chargeback_count DESC, chargeback_amount_inr DESC;

-- Output 5
/** merchant_id	merchant_name	category	chargeback_count	chargeback_amount_inr
"39"	"Merchant_039"	"entertainment"	"3"	"10997"
"27"	"Merchant_027"	"ecommerce"	"3"	"4047"
"29"	"Merchant_029"	"ecommerce"	"3"	"3897"
"40"	"Merchant_040"	"entertainment"	"2"	"5148"
"10"	"Merchant_010"	"grocery"	"2"	"5048"
"13"	"Merchant_013"	"travel"	"1"	"4999"
"19"	"Merchant_019"	"grocery"	"1"	"4999"
"25"	"Merchant_025"	"travel"	"1"	"2999"
"7"	"Merchant_007"	"food_delivery"	"1"	"1999"
"23"	"Merchant_023"	"travel"	"1"	"1999"
"28"	"Merchant_028"	"ecommerce"	"1"	"1999"
"32"	"Merchant_032"	"food_delivery"	"1"	"1999"
"37"	"Merchant_037"	"entertainment"	"1"	"1999"
"36"	"Merchant_036"	"entertainment"	"1"	"999"
"6"	"Merchant_006"	"food_delivery"	"1"	"799"
"3"	"Merchant_003"	"grocery"	"1"	"149"
"11"	"Merchant_011"	"ecommerce"	"1"	"149"
"24"	"Merchant_024"	"grocery"	"1"	"149"
"8"	"Merchant_008"	"food_delivery"	"1"	"49"
"31"	"Merchant_031"	"bill_payment"	"1"	"49"
**/

-- Query 6
SELECT m.merchant_id,
       m.merchant_name,
       COUNT(t.transaction_id) AS transaction_count
FROM merchants AS m
LEFT JOIN transactions AS t
    ON m.merchant_id = t.merchant_id
GROUP BY m.merchant_id, m.merchant_name
ORDER BY transaction_count DESC, m.merchant_id;

-- Output 6
/** merchant_id	merchant_name	transaction_count
"16"	"Merchant_016"	"20"
"29"	"Merchant_029"	"19"
"37"	"Merchant_037"	"19"
"9"	"Merchant_009"	"18"
"3"	"Merchant_003"	"17"
"25"	"Merchant_025"	"17"
"30"	"Merchant_030"	"17"
"7"	"Merchant_007"	"16"
"8"	"Merchant_008"	"16"
"22"	"Merchant_022"	"16"
"27"	"Merchant_027"	"16"
"34"	"Merchant_034"	"16"
"36"	"Merchant_036"	"16"
"31"	"Merchant_031"	"15"
"40"	"Merchant_040"	"15"
"6"	"Merchant_006"	"14"
"10"	"Merchant_010"	"14"
"19"	"Merchant_019"	"14"
"21"	"Merchant_021"	"14"
"32"	"Merchant_032"	"14"
"35"	"Merchant_035"	"14"
"12"	"Merchant_012"	"13"
"17"	"Merchant_017"	"13"
"24"	"Merchant_024"	"13"
"39"	"Merchant_039"	"13"
"13"	"Merchant_013"	"12"
"14"	"Merchant_014"	"12"
"15"	"Merchant_015"	"12"
"26"	"Merchant_026"	"12"
"5"	"Merchant_005"	"11"
"18"	"Merchant_018"	"11"
"33"	"Merchant_033"	"11"
"2"	"Merchant_002"	"10"
"11"	"Merchant_011"	"10"
"23"	"Merchant_023"	"10"
"28"	"Merchant_028"	"10"
"38"	"Merchant_038"	"10"
"1"	"Merchant_001"	"9"
"4"	"Merchant_004"	"9"
"20"	"Merchant_020"	"9"
**/

-- Query 7
SELECT u.user_id,
       t.transaction_id,
       u.signup_date,
       t.transaction_time,
       ROUND(julianday(t.transaction_time) - julianday(u.signup_date), 6)
           AS account_age_days,
       t.amount_inr,
       t.status
FROM users AS u
INNER JOIN transactions AS t
    ON u.user_id = t.user_id
WHERE t.status = 'chargeback'
  AND julianday(t.transaction_time) - julianday(u.signup_date) >= 0
  AND julianday(t.transaction_time) - julianday(u.signup_date) < 30
ORDER BY t.transaction_id;

-- Output 7 
/** user_id	transaction_id	signup_date	transaction_time	account_age_days	amount_inr	status
"351"	"TXN200000"	"2026-01-15 06:00:00"	"2026-01-30 06:00:00"	"15"	"1999"	"chargeback"
"352"	"TXN200001"	"2025-12-31 12:00:00"	"2026-01-11 12:00:00"	"11"	"4999"	"chargeback"
"353"	"TXN200002"	"2026-01-10 14:00:00"	"2026-01-21 14:00:00"	"11"	"1999"	"chargeback"
"354"	"TXN200003"	"2025-12-29 19:00:00"	"2026-01-21 19:00:00"	"23"	"4999"	"chargeback"
"355"	"TXN200004"	"2026-01-05 12:00:00"	"2026-01-16 12:00:00"	"11"	"4999"	"chargeback"
"356"	"TXN200005"	"2026-01-18 07:00:00"	"2026-01-29 07:00:00"	"11"	"2999"	"chargeback"
"357"	"TXN200006"	"2026-01-19 11:00:00"	"2026-01-23 11:00:00"	"4"	"1999"	"chargeback"
"358"	"TXN200007"	"2026-01-06 05:00:00"	"2026-01-28 05:00:00"	"22"	"999"	"chargeback"
"359"	"TXN200008"	"2026-01-18 22:00:00"	"2026-01-25 22:00:00"	"7"	"2999"	"chargeback"
"360"	"TXN200009"	"2025-12-22 13:00:00"	"2026-01-13 13:00:00"	"22"	"1999"	"chargeback"
"361"	"TXN200010"	"2026-01-11 07:00:00"	"2026-01-20 07:00:00"	"9"	"4999"	"chargeback"
"362"	"TXN200011"	"2026-01-08 02:00:00"	"2026-01-23 02:00:00"	"15"	"4999"	"chargeback"
"363"	"TXN200012"	"2026-01-06 17:00:00"	"2026-01-23 17:00:00"	"17"	"999"	"chargeback"
"364"	"TXN200013"	"2026-01-04 22:00:00"	"2026-01-22 22:00:00"	"18"	"999"	"chargeback"
"365"	"TXN200014"	"2025-12-27 21:00:00"	"2026-01-18 21:00:00"	"22"	"1999"	"chargeback"
**/

-- Query 8
SELECT user_id,
       datetime(
           transaction_time,
           printf(
               '-%d minutes',
               CAST(strftime('%M', transaction_time) AS INTEGER) % 10
           )
       ) AS ten_minute_bucket,
       MIN(transaction_time) AS cluster_start,
       MAX(transaction_time) AS cluster_end,
       COUNT(*) AS transaction_count
FROM transactions
GROUP BY user_id, ten_minute_bucket
HAVING COUNT(*) >= 3
ORDER BY user_id, cluster_start;

-- Output 8
/** user_id	ten_minute_bucket	cluster_start	cluster_end	transaction_count
"59"	"2026-01-09 21:00:00"	"2026-01-09 21:00:00"	"2026-01-09 21:03:00"	"4"
"73"	"2026-01-12 09:00:00"	"2026-01-12 09:00:00"	"2026-01-12 09:03:00"	"4"
"154"	"2026-01-02 22:00:00"	"2026-01-02 22:00:00"	"2026-01-02 22:03:00"	"4"
"200"	"2026-01-01 22:00:00"	"2026-01-01 22:00:00"	"2026-01-01 22:03:00"	"4"
"229"	"2026-01-12 12:00:00"	"2026-01-12 12:00:00"	"2026-01-12 12:03:00"	"4"
"287"	"2026-01-14 14:00:00"	"2026-01-14 14:00:00"	"2026-01-14 14:03:00"	"4"
"314"	"2026-01-02 18:00:00"	"2026-01-02 18:00:00"	"2026-01-02 18:03:00"	"4"
"345"	"2026-01-23 09:00:00"	"2026-01-23 09:00:00"	"2026-01-23 09:03:00"	"4"
**/