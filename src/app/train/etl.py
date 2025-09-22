#!/usr/bin/env python3
"""
Script para generar datos sintéticos de usuarios para targeting de promociones.
Este script simula un dataset realista para el problema de identificar qué usuarios
deben recibir promociones basado en su comportamiento transaccional y perfil.
"""

import json
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


class UserGenerator:
    def __init__(self, n_samples=1000, seed=42):
        self.n_samples = n_samples
        self.seed = seed

    def generate_synthetic_users(self):
        """
        Genera datos sintéticos de usuarios para targeting de promociones.
        
        Args:
            n_samples (int): Número de usuarios a generar
            seed (int): Semilla para reproducibilidad
        
        Returns:
            pd.DataFrame: Dataset con usuarios sintéticos
        """
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        # Definir categorías y valores posibles
        age_groups = ['18-25', '26-35', '36-45', '46-55', '55+']
        locations = ['Buenos Aires', 'Cordoba', 'Rosario', 'Mendoza', 'La Plata', 'Otros']
        device_types = ['Mobile', 'Desktop', 'Tablet']
        subscription_types = ['Free', 'Basic', 'Premium', 'Enterprise']
        
        # Generar fechas (últimos 12 meses)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Generar datos sintéticos
        data = []
        
        for i in range(self.n_samples):
            # Fecha de registro
            registration_date = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days)
            )
            
            # Días desde registro
            days_since_registration = (end_date - registration_date).days
            
            # Perfil del usuario
            age_group = random.choices(age_groups, weights=[0.25, 0.30, 0.25, 0.15, 0.05])[0]
            location = random.choices(locations, weights=[0.35, 0.20, 0.15, 0.10, 0.10, 0.10])[0]
            device_type = random.choices(device_types, weights=[0.60, 0.30, 0.10])[0]
            subscription_type = random.choices(subscription_types, weights=[0.40, 0.30, 0.25, 0.05])[0]
            
            # Comportamiento transaccional
            total_purchases = random.randint(0, 50)
            avg_order_value = random.uniform(10, 500)
            last_purchase_days = random.randint(0, 180) if total_purchases > 0 else 999
            
            # Métricas de engagement
            sessions_last_30_days = random.randint(0, 30)
            time_on_site_minutes = random.uniform(1, 120)
            pages_per_session = random.uniform(1, 20)
            
            # Métricas de conversión
            cart_abandonment_rate = random.uniform(0, 0.8)
            purchase_frequency = total_purchases / max(days_since_registration / 30, 1)
            
            # Crear registro
            record = {
                'user_id': f'USER-{i+1:06d}',
                'age_group': age_group,
                'location': location,
                'device_type': device_type,
                'subscription_type': subscription_type,
                'days_since_registration': days_since_registration,
                'total_purchases': total_purchases,
                'avg_order_value': round(avg_order_value, 2),
                'last_purchase_days': last_purchase_days,
                'sessions_last_30_days': sessions_last_30_days,
                'time_on_site_minutes': round(time_on_site_minutes, 1),
                'pages_per_session': round(pages_per_session, 1),
                'cart_abandonment_rate': round(cart_abandonment_rate, 3),
                'purchase_frequency': round(purchase_frequency, 2)
            }
            
            data.append(record)
        
        return pd.DataFrame(data)

    def add_missing_data(self, df):
        """
        Agrega valores nulos aleatorios para simular datos reales con missing values.
        
        Args:
            df (pd.DataFrame): DataFrame original
        
        Returns:
            pd.DataFrame: DataFrame con valores nulos agregados
        """
        # Definir campos y probabilidades de valores nulos
        null_config = {
            'age_group': 0.05,        # 5% de usuarios sin edad
            'location': 0.03,         # 3% de usuarios sin ubicación
            'device_type': 0.02,      # 2% de usuarios sin tipo de dispositivo
            'subscription_type': 0.01, # 1% de usuarios sin tipo de suscripción
            'avg_order_value': 0.08,   # 8% de usuarios sin valor promedio (usuarios nuevos)
            'last_purchase_days': 0.15, # 15% de usuarios sin última compra
            'time_on_site_minutes': 0.10, # 10% de usuarios sin tiempo en sitio
            'pages_per_session': 0.10,    # 10% de usuarios sin páginas por sesión
            'cart_abandonment_rate': 0.12, # 12% de usuarios sin tasa de abandono
            'purchase_frequency': 0.08     # 8% de usuarios sin frecuencia de compra
        }
        
        df_with_nulls = df.copy()
        
        for column, null_prob in null_config.items():
            if column in df_with_nulls.columns:
                # Generar máscara de valores nulos
                null_mask = np.random.random(len(df_with_nulls)) < null_prob
                
                # Aplicar valores nulos
                df_with_nulls.loc[null_mask, column] = np.nan
                
                print(f"✅ Agregados {null_mask.sum()} valores nulos en '{column}' ({null_prob*100:.1f}%)")
        
        return df_with_nulls

    def create_dataset(self):
        """Función principal para generar y guardar los datos."""
        print("Generando datos sintéticos de usuarios para targeting de promociones...")
        
        # Generar datos
        df = self.generate_synthetic_users()
        
        df = self.add_missing_data(df)
        
        # Crear variable target
        df["dar_promocion"] = random.choices([0, 1], k=len(df))
        
        # Guardar datos
        #output_file = 'usuarios_promociones.csv'
        #df.to_csv(output_file, index=False, encoding='utf-8')
        
        return df

