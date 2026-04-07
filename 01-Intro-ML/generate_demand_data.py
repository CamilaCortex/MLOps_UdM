#!/usr/bin/env python3
"""
Script para generar datos sintéticos de demanda diaria de un e-commerce.
Simula ventas con estacionalidad semanal, tendencia, eventos especiales
y ruido para practicar regresión con datos temporales.
"""

import random

import numpy as np
import pandas as pd


class DemandGenerator:
    def __init__(self, n_days=730, seed=42):
        """
        Args:
            n_days: Número de días a generar (default: 730 = 2 años).
            seed: Semilla para reproducibilidad.
        """
        self.n_days = n_days
        self.seed = seed

    def generate_daily_demand(self):
        """
        Genera datos sintéticos de demanda diaria con:
        - Estacionalidad semanal (más ventas viernes/sábado)
        - Estacionalidad mensual (más ventas en diciembre, menos en enero)
        - Tendencia creciente
        - Eventos especiales (Hot Sale, Black Friday, Navidad)
        - Clima simulado (afecta compras)
        - Campañas de marketing con efecto retardado

        Returns:
            pd.DataFrame: Dataset con demanda diaria.
        """
        np.random.seed(self.seed)
        random.seed(self.seed)

        start_date = pd.Timestamp("2023-01-01")
        dates = pd.date_range(start=start_date, periods=self.n_days, freq="D")

        data = []
        base_demand = 200  # demanda base diaria

        for i, date in enumerate(dates):
            # --- Tendencia: crecimiento gradual del negocio ---
            trend = i * 0.15  # +0.15 unidades por día

            # --- Estacionalidad semanal ---
            dow = date.dayofweek  # 0=lunes, 6=domingo
            weekly_effect = {
                0: -20,   # lunes: bajo
                1: -10,   # martes
                2: 0,     # miércoles
                3: 10,    # jueves
                4: 30,    # viernes: alto
                5: 40,    # sábado: pico
                6: 15,    # domingo: moderado
            }[dow]

            # --- Estacionalidad mensual ---
            month = date.month
            monthly_effect = {
                1: -30,   # enero: vacaciones, baja
                2: -15,
                3: 0,
                4: 5,
                5: 15,    # mayo: Hot Sale
                6: -10,   # junio: invierno
                7: -15,
                8: -5,
                9: 10,
                10: 15,
                11: 30,   # noviembre: Black Friday
                12: 50,   # diciembre: fiestas
            }[month]

            # --- Eventos especiales (binario) ---
            is_special_event = 0
            # Hot Sale (segunda semana de mayo)
            if month == 5 and 8 <= date.day <= 14:
                is_special_event = 1
            # Black Friday (cuarta semana de noviembre)
            elif month == 11 and 20 <= date.day <= 27:
                is_special_event = 1
            # Navidad (15-25 diciembre)
            elif month == 12 and 15 <= date.day <= 25:
                is_special_event = 1

            special_event_effect = is_special_event * np.random.uniform(80, 150)

            # --- Clima (temperatura simulada para hemisferio sur) ---
            # Más calor en diciembre-febrero, más frío en junio-agosto
            day_of_year = date.dayofyear
            temp_base = 22 - 10 * np.cos(2 * np.pi * (day_of_year - 15) / 365)
            temperature = temp_base + np.random.normal(0, 3)
            # Temperaturas extremas reducen demanda
            temp_effect = -0.5 * (temperature - 22) ** 2 / 50

            # --- Campañas de marketing ---
            # Simulamos campañas aleatorias con efecto que dura ~5 días
            has_campaign = 1 if random.random() < 0.08 else 0  # ~8% de los días
            campaign_spend = has_campaign * np.random.uniform(500, 3000)

            # --- Precio promedio del catálogo (varía ligeramente) ---
            avg_price = 1500 + np.random.normal(0, 100)
            # Efecto: precio más alto → menos demanda
            price_effect = -0.02 * (avg_price - 1500)

            # --- Calcular demanda ---
            demand = (
                base_demand
                + trend
                + weekly_effect
                + monthly_effect
                + special_event_effect
                + temp_effect
                + campaign_spend * 0.03  # ROI de marketing
                + price_effect
                + np.random.normal(0, 25)  # ruido
            )

            demand = max(int(round(demand)), 0)  # no negativo

            record = {
                "date": date,
                "units_sold": demand,
                "day_of_week": dow,
                "month": month,
                "is_weekend": 1 if dow >= 5 else 0,
                "is_special_event": is_special_event,
                "temperature": round(temperature, 1),
                "has_campaign": has_campaign,
                "campaign_spend": round(campaign_spend, 2),
                "avg_catalog_price": round(avg_price, 2),
                "days_since_start": i,
            }

            data.append(record)

        return pd.DataFrame(data)

    def add_missing_data(self, df):
        """Agrega valores nulos para simular datos reales."""
        df_with_nulls = df.copy()

        null_config = {
            "temperature": 0.05,       # 5% sin datos de clima
            "campaign_spend": 0.03,    # 3% sin registro de gasto
            "avg_catalog_price": 0.04, # 4% sin precio promedio
        }

        for column, null_prob in null_config.items():
            null_mask = np.random.random(len(df_with_nulls)) < null_prob
            df_with_nulls.loc[null_mask, column] = np.nan
            print(
                f"  Agregados {null_mask.sum()} valores nulos "
                f"en '{column}' ({null_prob*100:.1f}%)"
            )

        return df_with_nulls

    def add_lag_features(self, df):
        """
        Agrega features de rezago (lag) que son fundamentales en series
        temporales: la demanda de ayer, de hace 7 días, y promedios móviles.

        IMPORTANTE: estos lags se calculan ANTES del split porque representan
        información que SÍ estaría disponible en producción (son datos del
        pasado). No es data leakage.
        """
        df = df.copy()

        # Demanda del día anterior
        df["units_sold_lag_1"] = df["units_sold"].shift(1)

        # Demanda de hace 7 días (mismo día de la semana pasada)
        df["units_sold_lag_7"] = df["units_sold"].shift(7)

        # Promedio móvil de los últimos 7 días
        df["units_sold_rolling_7"] = (
            df["units_sold"].shift(1).rolling(window=7).mean()
        )

        # Promedio móvil de los últimos 30 días
        df["units_sold_rolling_30"] = (
            df["units_sold"].shift(1).rolling(window=30).mean()
        )

        return df

    def create_dataset(self, save_csv=True, output_file="demanda_diaria.csv"):
        """Función principal para generar y guardar los datos."""
        print("Generando datos sintéticos de demanda diaria...")

        df = self.generate_daily_demand()
        df = self.add_missing_data(df)
        df = self.add_lag_features(df)

        # Eliminar las primeras 30 filas (no tienen lags completos)
        df = df.iloc[30:].reset_index(drop=True)
        print(f"\n  Eliminadas las primeras 30 filas (lags incompletos)")
        print(f"  Dataset final: {df.shape[0]} filas, {df.shape[1]} columnas")

        if save_csv:
            df.to_csv(output_file, index=False, encoding="utf-8")
            print(f"  Guardado en: {output_file}")

        return df


if __name__ == "__main__":
    generator = DemandGenerator(seed=42, n_days=730)
    df = generator.create_dataset(save_csv=True)
    print(f"\nRango de fechas: {df['date'].min()} → {df['date'].max()}")
    print(f"Demanda promedio: {df['units_sold'].mean():.0f} unidades/día")
