from django.db import models
import uuid
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from datetime import datetime, date, timedelta
import json


class Maquina(models.Model):
    # CATEGORÍA 1: IDENTIFICACIÓN Y ESTATUS
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    TIPO_MAQUINA = [
        ('Defender', 'Defender'),
        ('Challenger', 'Challenger'),
    ]
    tipo = models.CharField("Tipo de Máquina", max_length=15, choices=TIPO_MAQUINA, default='Challenger', help_text="Defender (existente) o Challenger (potencial)")
    nombre = models.CharField("Nombre de la Máquina", max_length=100)
    numero_serie = models.CharField("Número de Serie", max_length=100, blank=True, null=True)
    criticality_ranking = models.FloatField("Ranking de Criticidad", blank=True, null=True)
    availability = models.FloatField("Disponibilidad (%)", blank=True, null=True)
    date_in_service = models.DateField("Fecha de Puesta en Servicio", blank=True, null=True)
    
    # CATEGORÍA 2: COSTOS DE ADQUISICIÓN Y VALOR
    purchase_price = models.DecimalField("Precio de Compra", max_digits=20, decimal_places=2, blank=True, null=True)
    installation_and_training_cost = models.DecimalField("Costo de Instalación y Formación", max_digits=20, decimal_places=2, blank=True, null=True)
    setup_costs = models.DecimalField("Costos de Configuración", max_digits=20, decimal_places=2, blank=True, null=True)
    current_resale_value = models.DecimalField("Valor de Reventa Actual", max_digits=20, decimal_places=2, blank=True, null=True)
    salvage_value = models.DecimalField("Valor Residual", max_digits=20, decimal_places=2, blank=True, null=True)
    # Campos adicionales necesarios:
    acquisition_cost = models.DecimalField("Costo de Adquisición (para Defender)", max_digits=20, decimal_places=2, blank=True, null=True)
    book_value = models.DecimalField("Valor en Libros", max_digits=20, decimal_places=2, blank=True, null=True)

    equipment_number = models.CharField("Número de Equipo", max_length=50, blank=True, null=True)
    # CATEGORÍA 3: COSTOS OPERATIVOS Y MANTENIMIENTO
    annual_maintenance_labor_parts = models.DecimalField("Mantenimiento Anual (Mano de Obra y Piezas)", max_digits=20, decimal_places=2, blank=True, null=True)
    initial_monthly_maintenance_cost = models.DecimalField("Costo Mensual Inicial de Mantenimiento", max_digits=20, decimal_places=2, blank=True, null=True)
    maintenance_cost_gradient = models.FloatField("Aumento Mensual del Costo de Mantenimiento", blank=True, null=True)
    cost_of_downtime = models.DecimalField("Costo de Inactividad ($/h)", max_digits=20, decimal_places=2, blank=True, null=True)
    operator_labor_cost = models.DecimalField("Costo de Mano de Obra del Operador ($/h)", max_digits=20, decimal_places=2, blank=True, null=True)
    energy_consumption = models.FloatField("Consumo de Energía (kWh/h)", blank=True, null=True)
    energy_cost = models.DecimalField("Costo de Energía ($/kWh)", max_digits=20, decimal_places=2, blank=True, null=True)
    consumable_replacement_cost_1 = models.DecimalField("Costo de Reemplazo de Consumible", max_digits=20, decimal_places=2, blank=True, null=True)
    consumable_lifespan_1 = models.FloatField("Vida Útil del Consumible (unidades)", blank=True, null=True)

    # CATEGORÍA 4: PRODUCCIÓN Y VIDA ÚTIL
    useful_life = models.IntegerField("Vida Útil (meses)", blank=True, null=True)
    end_of_useful_life_date = models.DateField("Fecha de Fin de Vida Útil", blank=True, null=True)
    monthly_depreciation = models.DecimalField("Depreciación Mensual", max_digits=20, decimal_places=2, blank=True, null=True)
    production_rate = models.FloatField("Tasa de Producción", blank=True, null=True)
    production_rate_units = models.CharField("Unidades de Tasa de Producción", max_length=50, blank=True, null=True, help_text="Ej: piezas/hora")
    texas_workdays = models.IntegerField("Días de Trabajo (Texas)", blank=True, null=True)
    monthly_operating_hours = models.FloatField("Horas de Operación Mensuales", blank=True, null=True)

    class Meta:
        verbose_name = "Máquina"
        verbose_name_plural = "Máquinas"

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class AnalisisComparativo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_analisis = models.CharField("Nombre del Análisis", max_length=200)
    defender = models.ForeignKey(Maquina, related_name='analisis_como_defender', on_delete=models.CASCADE)
    challenger = models.ForeignKey(Maquina, related_name='analisis_como_challenger', on_delete=models.CASCADE)
    
    # Parámetros financieros
    wacc = models.DecimalField("WACC (Costo Promedio Ponderado de Capital)", max_digits=5, decimal_places=4, default=0.14)
    tax_rate = models.DecimalField("Tasa de Impuestos", max_digits=5, decimal_places=4, default=0.21)
    
    # Parámetros de financiamiento para Challenger
    financing_rate = models.DecimalField("Tasa de Financiamiento (%)", max_digits=5, decimal_places=2, default=7.5)
    financing_months = models.IntegerField("Meses de Financiamiento", default=60)
    
    # Resultados del análisis
    pv_defender = models.DecimalField("Valor Presente Defender", max_digits=20, decimal_places=2, blank=True, null=True)
    eac_defender = models.DecimalField("EAC Defender", max_digits=20, decimal_places=2, blank=True, null=True)
    pv_challenger = models.DecimalField("Valor Presente Challenger", max_digits=20, decimal_places=2, blank=True, null=True)
    eac_challenger = models.DecimalField("EAC Challenger", max_digits=20, decimal_places=2, blank=True, null=True)
    
    recomendacion = models.CharField("Recomendación", max_length=50, blank=True, null=True)  # "Defender" o "Challenger"
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Análisis Comparativo"
        verbose_name_plural = "Análisis Comparativos"

class FlujoCaja(models.Model):
    analisis = models.ForeignKey(AnalisisComparativo, related_name='flujos_caja', on_delete=models.CASCADE)
    tipo_equipo = models.CharField(max_length=15, choices=[('Defender', 'Defender'), ('Challenger', 'Challenger')])
    año = models.IntegerField("Año")
    
    # Flujos de caja anuales
    cash_flow_bruto = models.DecimalField("Flujo de Caja Bruto", max_digits=20, decimal_places=2)
    depreciacion = models.DecimalField("Depreciación", max_digits=20, decimal_places=2)
    tax_shield = models.DecimalField("Escudo Fiscal", max_digits=20, decimal_places=2)
    after_tax_cash_flow = models.DecimalField("Flujo de Caja Después de Impuestos", max_digits=20, decimal_places=2)
    present_value = models.DecimalField("Valor Presente", max_digits=20, decimal_places=2)
    
    class Meta:
        verbose_name = "Flujo de Caja"
        verbose_name_plural = "Flujos de Caja"
        unique_together = ('analisis', 'tipo_equipo', 'año')

class TablaAmortizacion(models.Model):
    analisis = models.ForeignKey(AnalisisComparativo, related_name='tabla_amortizacion', on_delete=models.CASCADE)
    mes = models.IntegerField("Mes")
    
    balance_inicial = models.DecimalField("Balance Inicial", max_digits=20, decimal_places=2)
    pago_mensual = models.DecimalField("Pago Mensual", max_digits=20, decimal_places=2)
    pago_principal = models.DecimalField("Pago a Principal", max_digits=20, decimal_places=2)
    pago_interes = models.DecimalField("Pago de Interés", max_digits=20, decimal_places=2)
    balance_final = models.DecimalField("Balance Final", max_digits=20, decimal_places=2)
    
    class Meta:
        verbose_name = "Tabla de Amortización"
        verbose_name_plural = "Tablas de Amortización"
        unique_together = ('analisis', 'mes')

class Cliente(models.Model):
    id = models.CharField(max_length=50, primary_key=True, verbose_name="ID Cliente")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    terminos_contractuales = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Términos Contractuales (días)"
    )
    average_days_to_pay = models.IntegerField(default=0,
        validators=[MinValueValidator(1)],
        verbose_name="Días Promedio de Pago Real"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Creación")
    observaciones = models.TextField(blank=True, verbose_name="Descripción")
    def actualizar_dias_promedio_pago(self):
        from .models import Registro  # o el módulo donde esté Registro

        registros = self.registro_set.all()
        total_dias = 0
        total_pagos = 0

        for reg in registros:
            fecha_entrega = reg.fecha_entrega_cliente
            for pago in reg.obtener_pagos_cliente():
                fecha_pago = pago.get('fecha_pago')
                if fecha_pago:
                    if isinstance(fecha_pago, str):
                        try:
                            fecha_pago = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
                        except ValueError:
                            continue
                    
                    dias = (fecha_pago - fecha_entrega).days
                    if dias >= 0:
                        total_dias += dias
                        total_pagos += 1

        if total_pagos > 0:
            self.average_days_to_pay = total_dias // total_pagos
        else:
            self.average_days_to_pay = 1  # valor por defecto válido

        self.save()
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.id} - {self.nombre}"

class Proveedor(models.Model):
    id = models.CharField(max_length=50, primary_key=True, verbose_name="ID Proveedor")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    contacto = models.CharField(max_length=100, verbose_name="Contacto")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    terminos_pago = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Términos de Pago (días)"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Creación")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.id} - {self.nombre}"

class Registro(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado_parcial', 'Pagado Parcial'),
        ('pagado_total', 'Pagado Total'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
        ('tarjeta', 'Tarjeta'),
        ('otro', 'Otro')
    ]
    
    # Información básica del registro
    id = models.CharField(max_length=50, primary_key=True, verbose_name="ID Registro")
    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        verbose_name="Cliente"
    )
    fecha_entrega_cliente = models.DateField(verbose_name="Fecha Entrega Cliente")
    valor_cobrar_cliente = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor a Cobrar"
    )
    fecha_limite_cobro = models.DateField(
        verbose_name="Fecha Límite Cobro",
        editable=False,  # <-- AÑADE ESTO
        blank=True,      # <-- AÑADE ESTO para que no sea requerido al crear
        null=True        # <-- AÑADE ESTO para permitir valores nulos en la DB
    )
    estado_cobro = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado Cobro"
    )
    
    # Información de obligaciones/proveedores (solo almacenamiento)
    obligaciones_data = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Datos de Obligaciones",
        help_text="Lista de obligaciones con proveedores"
    )
    
    # Información de pagos de clientes (solo almacenamiento)
    pagos_cliente_data = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Datos de Pagos Cliente",
        help_text="Lista de pagos recibidos del cliente"
    )
    
    # Información de pagos a proveedores (solo almacenamiento)
    pagos_proveedor_data = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Datos de Pagos Proveedor",
        help_text="Lista de pagos realizados a proveedores"
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha Actualización")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    class Meta:
        verbose_name = "Registro"
        verbose_name_plural = "Registros"
        ordering = ['-fecha_creacion']
    
    def clean(self):
        """Validaciones básicas de coherencia"""
        super().clean()
        
        # Validar que la fecha límite sea después de la fecha de entrega
        if self.fecha_limite_cobro and self.fecha_entrega_cliente:
            if self.fecha_limite_cobro < self.fecha_entrega_cliente:
                raise ValidationError(
                    'La fecha límite de cobro no puede ser anterior a la fecha de entrega.'
                )
        
        # Validar estructura básica de los datos JSON
        self._validar_estructura_json()
    
    def _validar_estructura_json(self):
        """Valida que los datos JSON tengan la estructura correcta"""
        
        # Validar obligaciones_data
        if not isinstance(self.obligaciones_data, list):
            raise ValidationError('obligaciones_data debe ser una lista.')
        
        for obligacion in self.obligaciones_data:
            if not isinstance(obligacion, dict):
                raise ValidationError('Cada obligación debe ser un diccionario.')
            
            campos_requeridos = ['proveedor_nombre', 'valor_pagar']
            for campo in campos_requeridos:
                if campo not in obligacion:
                    raise ValidationError(f'La obligación debe tener el campo: {campo}')
        
        # Validar pagos_cliente_data
        if not isinstance(self.pagos_cliente_data, list):
            raise ValidationError('pagos_cliente_data debe ser una lista.')
        
        for pago in self.pagos_cliente_data:
            if not isinstance(pago, dict):
                raise ValidationError('Cada pago de cliente debe ser un diccionario.')
            
            campos_requeridos = ['monto', 'fecha_pago']
            for campo in campos_requeridos:
                if campo not in pago:
                    raise ValidationError(f'El pago de cliente debe tener el campo: {campo}')
        
        # Validar pagos_proveedor_data
        if not isinstance(self.pagos_proveedor_data, list):
            raise ValidationError('pagos_proveedor_data debe ser una lista.')
        
        for pago in self.pagos_proveedor_data:
            if not isinstance(pago, dict):
                raise ValidationError('Cada pago de proveedor debe ser un diccionario.')
            
            campos_requeridos = ['monto', 'fecha_pago', 'obligacion_id']
            for campo in campos_requeridos:
                if campo not in pago:
                    raise ValidationError(f'El pago de proveedor debe tener el campo: {campo}')
    
    def save(self, *args, **kwargs):
        """Guardar con lógica mínima"""
        # Calcular fecha límite de cobro automáticamente si no está definida
        if not self.fecha_limite_cobro and self.cliente and self.fecha_entrega_cliente:
            self.fecha_limite_cobro = self.fecha_entrega_cliente + timedelta(
                days=self.cliente.terminos_contractuales
            )
        
        super().save(*args, **kwargs)
    
    # ==================== MÉTODOS BÁSICOS DE ACCESO A DATOS ====================
    
    def agregar_obligacion(self, proveedor_nombre, valor_pagar, fecha_vencimiento, 
                          proveedor_id=None, descripcion="", referencia=""):
        """Agrega una nueva obligación al registro"""
        if not isinstance(self.obligaciones_data, list):
            self.obligaciones_data = []
        
        # Generar ID único basado en el índice
        nuevo_id = max(
            [int(obl.get('id', 0)) for obl in self.obligaciones_data if str(obl.get('id', '')).isdigit()],
            default=0
        ) + 1
        
        nueva_obligacion = {
            'id': nuevo_id,
            'proveedor_id': proveedor_id,
            'proveedor_nombre': proveedor_nombre,
            'valor_pagar': str(valor_pagar),
            'fecha_vencimiento': fecha_vencimiento.isoformat() if hasattr(fecha_vencimiento, 'isoformat') else str(fecha_vencimiento),
            'descripcion': descripcion,
            'referencia': referencia,
            'fecha_creacion': date.today().isoformat()
        }
        
        self.obligaciones_data.append(nueva_obligacion)
        self.save()
        return nueva_obligacion
    
    def agregar_pago_cliente(self, monto, fecha_pago, metodo_pago='transferencia', 
                            referencia="", observaciones=""):
        """Agrega un nuevo pago del cliente"""
        if not isinstance(self.pagos_cliente_data, list):
            self.pagos_cliente_data = []
        
        # Generar ID único
        nuevo_id = max([pago.get('id', 0) for pago in self.pagos_cliente_data], default=0) + 1
        
        nuevo_pago = {
            'id': nuevo_id,
            'monto': str(monto),
            'fecha_pago': fecha_pago.isoformat() if hasattr(fecha_pago, 'isoformat') else str(fecha_pago),
            'metodo_pago': metodo_pago,
            'referencia': referencia,
            'observaciones': observaciones,
            'fecha_registro': date.today().isoformat()
        }
        
        self.pagos_cliente_data.append(nuevo_pago)
        self.save()
        return nuevo_pago
    
    def agregar_pago_proveedor(self, obligacion_id, monto, fecha_pago, 
                              metodo_pago='transferencia', referencia="", observaciones=""):
        """Agrega un nuevo pago a proveedor"""
        if not isinstance(self.pagos_proveedor_data, list):
            self.pagos_proveedor_data = []
        
        # Generar ID único
        nuevo_id = max([pago.get('id', 0) for pago in self.pagos_proveedor_data], default=0) + 1
        
        nuevo_pago = {
            'id': nuevo_id,
            'obligacion_id': obligacion_id,
            'monto': str(monto),
            'fecha_pago': fecha_pago.isoformat() if hasattr(fecha_pago, 'isoformat') else str(fecha_pago),
            'metodo_pago': metodo_pago,
            'referencia': referencia,
            'observaciones': observaciones,
            'fecha_registro': date.today().isoformat()
        }
        
        self.pagos_proveedor_data.append(nuevo_pago)
        self.save()
        return nuevo_pago
    
    # ==================== MÉTODOS BÁSICOS DE CONSULTA ====================
    
    def obtener_obligaciones(self):
        """Retorna la lista de obligaciones"""
        return self.obligaciones_data or []
    
    def obtener_pagos_cliente(self):
        """Retorna la lista de pagos del cliente"""
        return self.pagos_cliente_data or []
    
    def obtener_pagos_proveedor(self):
        """Retorna la lista de pagos a proveedores"""
        return self.pagos_proveedor_data or []
    
    def obtener_obligacion(self, obligacion_id):
        """Obtiene una obligación específica por ID"""
        for obligacion in self.obtener_obligaciones():
            if obligacion.get('id') == obligacion_id:
                return obligacion
        return None
    
    def obtener_pagos_de_obligacion(self, obligacion_id):
        """Retorna los pagos de una obligación específica"""
        return [pago for pago in self.obtener_pagos_proveedor() 
                if pago.get('obligacion_id') == obligacion_id]
    
    # ==================== MÉTODOS BÁSICOS DE ELIMINACIÓN ====================
    
    def eliminar_obligacion(self, obligacion_id):
        """Elimina una obligación específica"""
        self.obligaciones_data = [
            obl for obl in self.obligaciones_data 
            if obl.get('id') != obligacion_id
        ]
        self.save()
    
    def eliminar_pago_cliente(self, pago_id):
        """Elimina un pago del cliente"""
        self.pagos_cliente_data = [
            pago for pago in self.pagos_cliente_data 
            if pago.get('id') != pago_id
        ]
        self.save()
    
    def eliminar_pago_proveedor(self, pago_id):
        """Elimina un pago a proveedor"""
        self.pagos_proveedor_data = [
            pago for pago in self.pagos_proveedor_data 
            if pago.get('id') != pago_id
        ]
        self.save()
    
    # ==================== PROPIEDADES BÁSICAS ====================
    
    @property
    def dias_vencimiento(self):
        """Retorna los días hasta/desde vencimiento (información básica)"""
        if not self.fecha_limite_cobro:
            return None
        delta = self.fecha_limite_cobro - date.today()
        return delta.days
    
    @property
    def esta_vencido(self):
        """Retorna True si el registro está vencido"""
        dias = self.dias_vencimiento
        return dias is not None and dias < 0 and self.estado_cobro != 'pagado_total'
    
    def __str__(self):
        return f"{self.id} - {self.cliente.nombre if self.cliente else 'Sin cliente'}"
    
    
    def calcular_fecha_limite_cobro(self):
        """Calcula la fecha límite de cobro basada en la fecha de entrega + términos del cliente"""
        if self.fecha_entrega_cliente and self.cliente:
            return self.fecha_entrega_cliente + timedelta(days=self.cliente.terminos_contractuales)
        return self.fecha_limite_cobro

    def calcular_saldo_pendiente_cliente(self):
        """Calcula el saldo pendiente de cobro al cliente"""
        pagos_realizados = sum(
            Decimal(str(pago.get('monto', 0))) 
            for pago in self.obtener_pagos_cliente()
        )
        return self.valor_cobrar_cliente - pagos_realizados

    def calcular_total_obligaciones(self):
        """Calcula el total de obligaciones pendientes"""
        total = Decimal('0')
        for obligacion in self.obtener_obligaciones():
            pagos_realizados = sum(
                Decimal(str(pago.get('monto', 0))) 
                for pago in self.obtener_pagos_de_obligacion(obligacion.get('id'))
            )
            valor_obligacion = Decimal(str(obligacion.get('valor_pagar', 0)))
            saldo_pendiente = valor_obligacion - pagos_realizados
            if saldo_pendiente > 0:
                total += saldo_pendiente
        return total

    def obtener_obligaciones_por_fecha_vencimiento(self, fecha_objetivo):
        """Obtiene las obligaciones que vencen en una fecha específica"""
        obligaciones_vencen = []
        
        for obligacion in self.obtener_obligaciones():
            fecha_vencimiento_str = obligacion.get('fecha_vencimiento')
            if fecha_vencimiento_str:
                try:
                    fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()
                    if fecha_vencimiento == fecha_objetivo:
                        # Calcular saldo pendiente
                        pagos_realizados = sum(
                            Decimal(str(pago.get('monto', 0))) 
                            for pago in self.obtener_pagos_de_obligacion(obligacion.get('id'))
                        )
                        valor_obligacion = Decimal(str(obligacion.get('valor_pagar', 0)))
                        saldo_pendiente = valor_obligacion - pagos_realizados
                        
                        if saldo_pendiente > 0:
                            obligacion_copia = obligacion.copy()
                            obligacion_copia['saldo_pendiente'] = saldo_pendiente
                            obligacion_copia['pagos_realizados'] = pagos_realizados
                            obligaciones_vencen.append(obligacion_copia)
                except ValueError:
                    continue
        
        return obligaciones_vencen

    def generar_obligacion_con_fecha_vencimiento(self, proveedor_id, proveedor_nombre, valor_pagar, 
                                            fecha_recepcion, descripcion="", referencia=""):
        """Genera una obligación calculando automáticamente la fecha de vencimiento"""
        
        # Obtener el proveedor para conocer sus términos de pago
        try:
            from .models import Proveedor  # Ajusta la importación según tu estructura
            proveedor = Proveedor.objects.get(id=proveedor_id)
            
            # Calcular fecha de vencimiento
            if isinstance(fecha_recepcion, str):
                fecha_recepcion = datetime.strptime(fecha_recepcion, '%Y-%m-%d').date()
            
            fecha_vencimiento = fecha_recepcion + timedelta(days=proveedor.terminos_pago)
            
            # Crear la obligación
            return self.agregar_obligacion(
                proveedor_nombre=proveedor_nombre,
                valor_pagar=valor_pagar,
                fecha_vencimiento=fecha_vencimiento,
                proveedor_id=proveedor_id,
                descripcion=descripcion,
                referencia=referencia
            )
            
        except Exception as e:
            # Si no se puede obtener el proveedor, usar fecha de vencimiento manual
            return self.agregar_obligacion(
                proveedor_nombre=proveedor_nombre,
                valor_pagar=valor_pagar,
                fecha_vencimiento=fecha_recepcion + timedelta(days=30),  # Default 30 días
                proveedor_id=proveedor_id,
                descripcion=descripcion,
                referencia=referencia
            )

    def actualizar_estado_cobro(self):
        """Actualiza automáticamente el estado de cobro basado en los pagos recibidos"""
        saldo_pendiente = self.calcular_saldo_pendiente_cliente()
        
        if saldo_pendiente <= 0:
            self.estado_cobro = 'pagado_total'
        elif saldo_pendiente < self.valor_cobrar_cliente:
            self.estado_cobro = 'pagado_parcial'
        else:
            self.estado_cobro = 'pendiente'
        
        self.save()

    def obtener_proyeccion_flujo(self, fecha_inicio, fecha_fin):
        """Obtiene la proyección del flujo de caja para este registro en un período específico"""
        flujo_proyectado = []
        
        # Proyección de ingreso (fecha límite de cobro)
        fecha_limite = self.calcular_fecha_limite_cobro()
        if fecha_limite and fecha_inicio <= fecha_limite <= fecha_fin:
            saldo_pendiente = self.calcular_saldo_pendiente_cliente()
            if saldo_pendiente > 0:
                flujo_proyectado.append({
                    'fecha': fecha_limite,
                    'tipo': 'ingreso',
                    'monto': float(saldo_pendiente),
                    'concepto': f'Cobro a {self.cliente.nombre}',
                    'registro_id': self.id
                })
        
        # Proyección de egresos (obligaciones)
        for obligacion in self.obtener_obligaciones():
            fecha_vencimiento_str = obligacion.get('fecha_vencimiento')
            if fecha_vencimiento_str:
                try:
                    fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()
                    if fecha_inicio <= fecha_vencimiento <= fecha_fin:
                        pagos_realizados = sum(
                            Decimal(str(pago.get('monto', 0))) 
                            for pago in self.obtener_pagos_de_obligacion(obligacion.get('id'))
                        )
                        valor_obligacion = Decimal(str(obligacion.get('valor_pagar', 0)))
                        saldo_pendiente = valor_obligacion - pagos_realizados
                        
                        if saldo_pendiente > 0:
                            flujo_proyectado.append({
                                'fecha': fecha_vencimiento,
                                'tipo': 'egreso',
                                'monto': float(saldo_pendiente),
                                'concepto': f'Pago a {obligacion.get("proveedor_nombre")}',
                                'registro_id': self.id,
                                'obligacion_id': obligacion.get('id')
                            })
                except ValueError:
                    continue
        
        return flujo_proyectado

    # ==================== PROPIEDADES ADICIONALES ====================

    @property
    def rentabilidad_estimada(self):
        """Calcula la rentabilidad estimada como porcentaje del margen bruto fijo"""
        if self.valor_cobrar_cliente > 0:
            return (self.margen_bruto / self.valor_cobrar_cliente) * 100
        return 0

    @property
    def margen_bruto(self):
        """Calcula el margen bruto fijo del registro (valor cliente - total obligaciones originales)"""
        total_obligaciones_originales = sum(
            Decimal(str(obl.get('valor_pagar', 0))) 
            for obl in self.obtener_obligaciones()
        )
        return self.valor_cobrar_cliente - total_obligaciones_originales

    @property
    def porcentaje_cobrado(self):
        """Calcula el porcentaje cobrado del valor total"""
        if self.valor_cobrar_cliente > 0:
            pagos_realizados = sum(
                Decimal(str(pago.get('monto', 0))) 
                for pago in self.obtener_pagos_cliente()
            )
            return (pagos_realizados / self.valor_cobrar_cliente) * 100
        return 0

    @property
    def porcentaje_pagado_proveedores(self):
        """Calcula el porcentaje pagado a proveedores"""
        total_obligaciones = sum(
            Decimal(str(obl.get('valor_pagar', 0))) 
            for obl in self.obtener_obligaciones()
        )
        
        if total_obligaciones > 0:
            total_pagado = sum(
                Decimal(str(pago.get('monto', 0))) 
                for pago in self.obtener_pagos_proveedor()
            )
            return (total_pagado / total_obligaciones) * 100
        return 0

    @property
    def dias_promedio_cobro(self):
        """Calcula los días promedio de cobro basado en pagos realizados"""
        pagos_cliente = self.obtener_pagos_cliente()
        if not pagos_cliente:
            return None
        
        total_dias = 0
        total_pagos = 0
        
        for pago in pagos_cliente:
            try:
                fecha_pago = datetime.strptime(pago.get('fecha_pago'), '%Y-%m-%d').date()
                dias_transcurridos = (fecha_pago - self.fecha_entrega_cliente).days
                monto_pago = Decimal(str(pago.get('monto', 0)))
                
                total_dias += dias_transcurridos * float(monto_pago)
                total_pagos += float(monto_pago)
            except (ValueError, TypeError):
                continue
        
        if total_pagos > 0:
            return total_dias / total_pagos
        return None

    # ==================== MÉTODOS DE ANÁLISIS ====================

    def analizar_riesgo_cobro(self):
        """Analiza el riesgo de cobro del registro"""
        if not self.fecha_limite_cobro:
            return {'nivel': 'sin_datos', 'mensaje': 'No hay fecha límite establecida'}
        
        dias_vencimiento = self.dias_vencimiento
        saldo_pendiente = self.calcular_saldo_pendiente_cliente()
        
        if saldo_pendiente <= 0:
            return {'nivel': 'sin_riesgo', 'mensaje': 'Pagado completamente'}
        
        if dias_vencimiento is None:
            return {'nivel': 'sin_datos', 'mensaje': 'No se puede calcular el riesgo'}
        
        if dias_vencimiento < -30:
            return {'nivel': 'critico', 'mensaje': f'Vencido hace más de 30 días'}
        elif dias_vencimiento < 0:
            return {'nivel': 'alto', 'mensaje': f'Vencido hace {abs(dias_vencimiento)} días'}
        elif dias_vencimiento <= 7:
            return {'nivel': 'medio', 'mensaje': f'Vence en {dias_vencimiento} días'}
        else:
            return {'nivel': 'bajo', 'mensaje': f'Vence en {dias_vencimiento} días'}

    def generar_reporte_flujo_individual(self):
        """Genera un reporte de flujo de caja individual para este registro"""
        return {
            'registro_id': self.id,
            'cliente': self.cliente.nombre if self.cliente else 'N/A',
            'fecha_entrega': self.fecha_entrega_cliente.isoformat(),
            'fecha_limite_cobro': self.fecha_limite_cobro.isoformat() if self.fecha_limite_cobro else None,
            'valor_total': float(self.valor_cobrar_cliente),
            'saldo_pendiente_cliente': float(self.calcular_saldo_pendiente_cliente()),
            'total_obligaciones': float(self.calcular_total_obligaciones()),
            'margen_bruto': float(self.margen_bruto),
            'rentabilidad_estimada': self.rentabilidad_estimada,
            'porcentaje_cobrado': self.porcentaje_cobrado,
            'porcentaje_pagado_proveedores': self.porcentaje_pagado_proveedores,
            'dias_vencimiento': self.dias_vencimiento,
            'riesgo_cobro': self.analizar_riesgo_cobro(),
            'estado_cobro': self.estado_cobro,
            'total_pagos_cliente': len(self.obtener_pagos_cliente()),
            'total_pagos_proveedor': len(self.obtener_pagos_proveedor()),
            'total_obligaciones_count': len(self.obtener_obligaciones())
        }
        
        