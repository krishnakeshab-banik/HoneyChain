"""Existing HoneyChain visual theme. Presentation only."""

from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none; }

        .stApp {
            background:
                linear-gradient(
                    180deg,
                    #FBFAF7 0%,
                    #F7F3EA 100%
                );
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        .brand {
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.18rem;
            color: #9A6A16;
            margin-bottom: 0.4rem;
        }
        .hero-title {
            font-size: 2.7rem;
            line-height: 1.05;
            font-weight: 750;
            color: #202020;
            margin-bottom: 0.7rem;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: #66615B;
            max-width: 750px;
            margin-bottom: 2rem;
        }
        .live-badge {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: #E8F3EB;
            color: #357047;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .section-label {
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.08rem;
            color: #807970;
            margin-top: 1.5rem;
            margin-bottom: 0.7rem;
        }
        .status-card {
            padding: 1.2rem 1.4rem;
            border-radius: 16px;
            background: white;
            border: 1px solid #E7E1D7;
            box-shadow: 0 6px 20px rgba(30, 25, 20, 0.04);
            margin-bottom: 1rem;
            color: #2A2723;
        }
        .status-card b {
            color: #24211E;
            font-size: 1.05rem;
        }
        [data-testid="stAppViewContainer"] { color: #26231F; }
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E7E1D7;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            box-shadow: 0 6px 18px rgba(30, 25, 20, 0.04);
        }
        [data-testid="stMetricLabel"] { color: #716A61 !important; }
        [data-testid="stMetricLabel"] p {
            color: #716A61 !important;
            font-weight: 600 !important;
        }
        [data-testid="stMetricValue"] { color: #24211E !important; }
        [data-testid="stMetricValue"] div { color: #24211E !important; }
        [data-testid="stCaptionContainer"] { color: #777068 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
