/**
 * 商机数据类型定义
 * 对齐后端数据模型：
 * - ASOpportunity (infrastructure/database/models/opportunities.py)
 * - IPGClient (infrastructure/database/models/opportunities.py)
 * - WorkOrder (infrastructure/database/models/work_orders.py)
 * - EnterpriseQDProfile (infrastructure/database/models/enterprise_qd.py)
 */

// ==================== AS商机 ====================
export interface ASOpportunity {
  id: number
  report_id?: number
  customer_name: string
  contact_person?: string
  mobile?: string
  phone?: string
  email?: string
  website?: string
  address?: string
  area?: string
  areaname?: string
  industry?: string
  product_name?: string
  budget?: number
  expected_close_date?: string
  status?: string
  statename?: string
  partner_name?: string
  creator?: string
  last_modifier?: string
  requirements?: string
  notes?: string
  create_time?: string
  last_modify_time?: string
  submit_time?: string
  data_source?: string
  created_at?: string
  updated_at?: string
}

// ==================== IPG客户 ====================
export interface IPGClient {
  id: number
  rid?: number
  client_name: string
  client_type?: string
  trade?: string
  trade2?: string
  contact?: string
  contact_position?: string
  contact_phone?: string
  contact_mobile?: string
  email?: string
  contact_addr?: string
  location_area?: string
  location_province?: string
  location_city?: string
  area_id?: number
  province_id?: number
  city_id?: number
  sell_product?: string
  agent_num?: number
  sell_cycle?: string
  rival?: string
  requirement?: string
  need_support?: string
  faith_in?: string
  remark?: string
  comments?: string
  status?: string
  status_id?: number
  sub_status?: number
  sub_status_txt?: string
  create_time?: string
  expiration_time?: string
  is_delay?: boolean
  is_have_first_trial?: boolean
  first_trial_days?: number
  first_trial_agent_num?: number
  first_trial_modules?: string
  first_trial_is_en?: string
  reseller_name?: string
  reseller_code?: string
  reseller_sale?: string
  data_source?: string
  created_at?: string
  updated_at?: string
}

// ==================== 企业档案(QD) ====================
export interface EnterpriseQD {
  name: string
  normalized_name?: string
  address?: string
  industry?: string
  region?: string
  employee_scale?: string
  revenue_2021?: number
  revenue_2022?: number
  revenue_2023?: number
  ranking_status?: Record<string, unknown>
  business_summary?: string
  ranking_description?: string
  confidence_score?: number
  is_complete?: boolean
  created_at?: string
  updated_at?: string
}

// ==================== 工单 ====================
export interface WorkOrder {
  record_id: string
  source_id?: string
  application_no?: string
  application_link?: string
  status?: string
  priority?: string
  workflow_name?: string
  customer_company?: string
  customer_contact?: string
  customer_phone_secondary?: string
  work_content?: string
  work_mode?: string
  work_type?: string
  engineer_identity?: string
  has_channel?: boolean
  channel_name?: string
  channel_contact?: string
  channel_phone_secondary?: string
  initiator_department?: string
  initiated_at?: string
  initiator_primary_id?: string
  initiator_primary_name?: string
  initiator_primary_email?: string
  completed_at?: string
  service_start_date?: string
  service_start_datetime?: string
  service_start_period?: string
  service_end_date?: string
  service_end_datetime?: string
  service_end_period?: string
  after_sales_engineer_primary_id?: string
  after_sales_engineer_primary_name?: string
  after_sales_engineer_primary_email?: string
  fetched_at?: string
  created_at?: string
  updated_at?: string
}

// ==================== API响应类型 ====================

export interface OpportunitiesSearchResponse {
  success: boolean
  company_name: string
  summary: {
    as_count: number
    ipg_count: number
    qd_count: number
    work_order_count: number
    total_count: number
  }
  data: {
    as_opportunities: ASOpportunity[]
    ipg_clients: IPGClient[]
    qd_enterprises: EnterpriseQD[]
    work_orders: WorkOrder[]
  }
}

export interface ASStatistics {
  total_count: number
  unique_customers: number
  unique_partners: number
  unique_areas: number
  total_budget: number
  avg_budget: number
  status_distribution: Record<string, number>
}

export interface IPGStatistics {
  total_count: number
  unique_clients: number
  unique_resellers: number
  unique_provinces: number
  total_agent_num: number
  avg_agent_num: number
  status_distribution: Record<string, number>
}

export interface AllStatistics {
  success: boolean
  data: {
    as: ASStatistics
    ipg: IPGStatistics
    total_opportunities: number
  }
}
