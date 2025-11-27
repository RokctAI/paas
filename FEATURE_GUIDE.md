# Feature Guide - PaaS Module

This document provides a comprehensive overview of the PaaS (Platform as a Service) module's capabilities. It covers both the core features and the newly migrated modules, serving as a complete reference for the system.

## 1. Core Platform

### Users & Authentication
*   **Users:** The system manages all users (Admins, Sellers, Customers, Delivery Men) in a unified `User` database.
*   **Roles:** Permissions are role-based. Common roles include "System Manager", "Seller", "Customer", and "Driver".
*   **Authentication:** Secure login and registration via email/password or social providers (if configured).

### Localization
*   **Languages:** Admins can manage supported languages (e.g., English, Arabic) and set a default. Supports RTL (Right-to-Left) layouts.
*   **Translations:** All app text can be translated dynamically via the `PaaS Translation` system, allowing for instant updates to UI text without app store releases.

## 2. E-Commerce & Catalog

### Shops (Restaurants/Stores)
*   **Management:** Sellers can create and manage their own Shops.
*   **Details:** Shops have names, descriptions, logos, cover images, and locations.
*   **Settings:** Shops can configure working hours, delivery times, and minimum order amounts.

### Products
*   **Catalog:** Shops list items with titles, descriptions, prices, and images.
*   **Categories:** Products are organized into categories (e.g., "Food", "Electronics") and sub-categories.
*   **Brands:** Products can be linked to specific Brands.
*   **Units:** Support for different units of measurement (kg, pcs, liters).
*   **Product Extras (Variants):**
    *   **Options:** Shops can define options like "Size" (Small, Large) or "Color".
    *   **Stock:** Specific variants (e.g., "Large Red Shirt") are tracked as individual `Stock` items with their own prices and SKUs.

## 3. Order Management

### Orders
*   **Lifecycle:** The system handles the full order lifecycle: `New` -> `Accepted` -> `Processing` -> `Ready` -> `On a Way` -> `Delivered`.
*   **Details:** Orders track items, quantities, prices, taxes, and delivery fees.
*   **Refunds:** Customers can request refunds, which Admins or Sellers can approve/reject.

### Booking System
*   **Reservations:** Customers can book tables at restaurants for specific dates and times.
*   **Slots:** Shops define "Booking Slots" (e.g., Lunch Shift 12pm-3pm) to control availability.
*   **Tables:** Shops manage their floor plan with Sections (e.g., Terrace) and Tables.

### Parcel Delivery
*   **Custom Deliveries:** Users can send packages between any two points.
*   **Configuration:** Admins define Parcel Types (e.g., "Small Box") with specific weight/size limits and pricing rules.
*   **Options:** Users can add extras like "Insurance" or "Express" for a fee.

## 4. Logistics & Delivery

### Delivery Zones
*   **Precision Areas:** Shops can draw custom polygons on a map to define exactly where they deliver.
*   **Dynamic Pricing:** Delivery fees are calculated based on the customer's distance from the shop (Base Price + Price per KM).

### Drivers & Vehicles
*   **Delivery Men:** Dedicated users who handle deliveries.
*   **Vehicles:** Drivers are assigned vehicles (Bike, Car, Van) which can determine which orders they can take (e.g., large parcels require a Van).

## 5. Financials

### Payments
*   **Gateways:** Support for multiple payment gateways (e.g., Stripe, Razorpay) via the `Payment` module.
*   **Wallets:** Every user has a digital Wallet. They can top up, pay for orders, or receive refunds into their wallet.
*   **Transactions:** All financial movements are recorded as immutable Transactions.

### Payouts
*   **Seller Payouts:** The platform tracks earnings for Sellers and facilitates payouts to their bank accounts.

## 6. Marketing & Engagement

### Promotions
*   **Banners:** Admins can place promotional banners on the app home screen.
*   **Coupons:** Create discount codes (fixed amount or percentage) for customers to use at checkout.
*   **Discounts:** Apply automatic discounts to specific products or categories.

### Ads Packages
*   **Monetization:** Shops can purchase "Ads Packages" (e.g., "7-Day Homepage Feature") from the Admin to boost their visibility.

### Content
*   **Blog:** Admins can publish blog posts and news updates.
*   **Notifications:** Send targeted push notifications to users (Web, Mobile, Drivers).
*   **FAQ:** Manage a searchable list of Frequently Asked Questions.

## 7. Support
*   **Tickets:** Users can open support tickets for issues with orders or the app. Admins can track and resolve these tickets.

---
*This guide serves as a high-level overview of the system's functionality.*
