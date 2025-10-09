# V2 Frontend Refactoring Documentation

**Date**: 2025-10-09
**Branch**: `feature/v2-frontend-refactor`
**Status**: ✅ Complete - Awaiting Manual Testing

## Overview

This document records the comprehensive refactoring of `city_brain_frontend_v2` to align with actual backend data sources and APIs. The original V2 frontend was designed with APIs that don't exist in the backend, causing significant misalignment.

## Problem Statement

### Original Issues

1. **Insights View**: Designed with time-series chart API (`/v1/insights/timeseries`) that doesn't exist
2. **Operations View**: Had create ticket form but backend only supports queries
3. **Planning View**: Designed for map layers and spatial data (no backend support)
4. **Admin View**: Permission management system (backend has no authentication)
5. **Dashboard**: Isolated company search without opportunities/work orders integration

### Data Misalignment

- Frontend expected non-existent endpoints
- TypeScript types didn't match Python backend models
- Missing integration with CRM data sources (AS/IPG/QD/WorkOrder)

## Solution Approach

### Guiding Principles

1. **Only use existing backend APIs** - Remove all features without backend support
2. **100% type alignment** - TypeScript interfaces must match Python dataclasses exactly
3. **Reusable components** - Create universal components for multiple data sources
4. **Progressive enhancement** - Keep code structure for future features (commented, not deleted)

## Changes Made

### 1. Type System Alignment

**File**: `src/types/opportunities.ts` (Created)

Created comprehensive TypeScript interfaces matching backend Python models:

```typescript
// AS System (448 records from feishu_crm.as_opportunities)
export interface ASOpportunity {
  id: number
  customer_name: string
  product_name?: string
  budget?: number
  status?: string
  partner_name?: string
  // ... 30+ fields matching Python ASOpportunity dataclass
}

// IPG System (1,678 records from feishu_crm.ipg_clients)
export interface IPGClient {
  id: number
  client_name: string
  trade?: string
  reseller_name?: string
  agent_num?: number
  // ... fields matching Python IPGClient dataclass
}

// QD Enterprise Archive (268 records from enterprise_QD)
export interface EnterpriseQD {
  company_name: string
  industry?: string
  annual_revenue?: number
  province_ranking?: number
  // ... fields matching Python EnterpriseQD dataclass
}

// Work Orders (86 records from Task_sync_new.task_service_records)
export interface WorkOrder {
  record_id: string
  workflow_name?: string
  customer_company?: string
  priority?: string
  status: string
  // ... fields matching Python WorkOrder dataclass
}
```

### 2. API Service Layer

**Files Created**:
- `src/services/opportunitiesService.ts` - Multi-source opportunities/work orders
- `src/services/insightsService.ts` (Refactored) - Statistics from backend
- `src/services/operationsService.ts` (Refactored) - Work order queries only

**Key Functions**:

```typescript
// Fetch all data sources for a company
export async function searchAllOpportunities(
  companyName: string,
  limitPerSource: number = 10
): Promise<OpportunitiesSearchResponse>

// Get AS/IPG statistics
export async function fetchAllStatistics(): Promise<AllStatistics>

// Search AS system
export async function searchASOpportunities(params): Promise<ASOpportunitySearchResponse>

// Search IPG system
export async function searchIPGClients(params): Promise<IPGClientSearchResponse>

// Search work orders
export async function searchWorkOrders(params): Promise<WorkOrderSearchResponse>
```

**Removed Functions**:
- ❌ `createOperationTicket()` - Backend only supports queries
- ❌ `fetchTimeSeriesData()` - API doesn't exist

### 3. State Management

**File**: `src/stores/opportunitiesStore.ts` (Created)

Pinia store for opportunities state:

```typescript
export const useOpportunitiesStore = defineStore('opportunities', {
  state: (): OpportunitiesState => ({
    searchResult: null,
    loading: false,
    error: undefined
  }),

  actions: {
    async searchOpportunities(companyName: string, limitPerSource: number = 10) {
      this.loading = true
      try {
        this.searchResult = await searchAllOpportunities(companyName, limitPerSource)
      } catch (err) {
        this.error = err
      } finally {
        this.loading = false
      }
    }
  },

  getters: {
    asOpportunities: (state) => state.searchResult?.data.as_opportunities || [],
    ipgClients: (state) => state.searchResult?.data.ipg_clients || [],
    qdEnterprises: (state) => state.searchResult?.data.qd_enterprises || [],
    workOrders: (state) => state.searchResult?.data.work_orders || []
  }
})
```

### 4. Reusable Components

#### OpportunityCard Component

**File**: `src/components/data/OpportunityCard.vue` (Created)

Universal card component for all data sources (AS/IPG/QD/WorkOrder):

**Props**:
- `title: string` - Card title
- `status?: string` - Status text with auto-color coding
- `badge: { text: string, type: 'as' | 'ipg' | 'qd' | 'work-order' }` - Badge config

**Features**:
- Default slot for content
- Footer slot for metadata
- Auto-detects status type for color (进行中=blue, 赢单=green, 输单=red, etc.)
- Badge type determines color scheme (AS=green, IPG=orange, QD=blue, WorkOrder=red)

**Usage**:
```vue
<OpportunityCard
  :title="opp.product_name || opp.customer_name"
  :status="opp.statename || opp.status"
  :badge="{ text: 'AS系统', type: 'as' }"
>
  <div class="detail-row">
    <span class="label">客户：</span>{{ opp.customer_name }}
  </div>
  <template #footer>
    <div>预算：¥{{ opp.budget?.toLocaleString() }}</div>
  </template>
</OpportunityCard>
```

#### StatisticsPanel Component

**File**: `src/components/data/StatisticsPanel.vue` (Created)

Statistics display with auto-formatting:

**Props**:
- `title: string` - Panel title
- `subtitle?: string` - Subtitle
- `statistics: Statistic[]` - Array of { label, value, format?, unit? }

**Supported Formats**:
- `number` - Formatted with thousands separator
- `currency` - Formatted as currency with unit
- `percentage` - Formatted as percentage

**Features**:
- Default slot for additional content
- Footer slot for extra info
- Responsive grid layout

### 5. View Refactoring

#### Dashboard View (Extended)

**File**: `src/views/dashboard/DashboardView.vue`

**Changes**:
- ✅ Added opportunities store integration
- ✅ Auto-loads related data when company is queried
- ✅ Displays AS/IPG/QD/WorkOrder in separate sections
- ✅ Uses OpportunityCard for all data sources

**Key Implementation**:
```typescript
import { useOpportunitiesStore } from '@stores/opportunitiesStore'

const opportunitiesStore = useOpportunitiesStore()
const companyStore = useCompanyStore()

// Auto-trigger opportunities search when company is found
watch(() => companyStore.result, (newResult) => {
  if (newResult?.company_name) {
    opportunitiesStore.searchOpportunities(newResult.company_name, 5)
  }
})
```

#### Insights View (Completely Refactored)

**File**: `src/views/insights/InsightsView.vue`

**Before**:
- Time-series charts with non-existent API
- Trend analysis features
- Historical data visualization

**After**:
- ✅ Statistics panels for AS/IPG systems
- ✅ Status distribution display
- ✅ Keyword search with tabular results
- ✅ System selector (AS/IPG)

**Data Flow**:
```
Load → fetchAllStatistics() → Display AS/IPG stats with status distribution
User search → searchASOpportunities() or searchIPGClients() → Display in DataTable
```

#### Operations View (Completely Refactored)

**File**: `src/views/operations/OperationsView.vue`

**Before**:
- Create ticket form (no backend support)
- Ticket type selector
- Assignment features

**After**:
- ✅ Search-only interface
- ✅ Work order cards with priority color coding
- ✅ Statistics panel (total, status, priority distribution)
- ✅ Engineer info display

**Features**:
- Priority color coding (高=red, 中=orange, 低=green)
- Status badges
- Engineer assignment info
- Initiated time display

#### Router Configuration

**File**: `src/router/index.ts`

**Changes**:
```typescript
// Planning route commented (no backend data)
// {
//   path: '/planning',
//   component: () => import('@views/planning/PlanningView.vue'),
//   meta: { title: '行业分析' }
// },

// Admin route removed (no authentication system)
```

**Active Routes**:
1. `/dashboard` - 企业信息查询
2. `/insights` - 商机洞察
3. `/operations` - 工单查询

#### Navigation Menu

**File**: `src/components/layout/SidebarNav.vue`

**Before**:
```typescript
const links = [
  { to: '/dashboard', label: '仪表盘', icon: '📊' },
  { to: '/insights', label: '洞察分析', icon: '🔍' },
  { to: '/operations', label: '运营管理', icon: '🧭' },
  { to: '/planning', label: '空间规划', icon: '🗺️' },
  { to: '/admin', label: '权限配置', icon: '⚙️' }
]
```

**After**:
```typescript
const links = [
  { to: '/dashboard', label: '企业信息查询', icon: '📊' },
  { to: '/insights', label: '商机洞察', icon: '🔍' },
  { to: '/operations', label: '工单查询', icon: '🧭' }
  // Planning路由已注释 - 后端无空间规划/图层数据
  // Admin路由已移除 - 后端无鉴权系统
]
```

## API Endpoints Used

### Backend Endpoints (All Verified)

| Endpoint | Method | Purpose | Data Source |
|----------|--------|---------|-------------|
| `/v1/company/process` | POST | Company info query | City_Brain_DB |
| `/v1/opportunities/search` | GET | Multi-source search | feishu_crm, enterprise_QD, Task_sync_new |
| `/v1/opportunities/statistics` | GET | AS/IPG statistics | feishu_crm |
| `/v1/opportunities/as/search` | GET | AS system search | feishu_crm.as_opportunities |
| `/v1/opportunities/ipg/search` | GET | IPG system search | feishu_crm.ipg_clients |

### Data Sources Summary

1. **AS Opportunities** (448 records)
   - Database: `feishu_crm.as_opportunities`
   - Search field: `customer_name`
   - Display: Green badge

2. **IPG Clients** (1,678 records)
   - Database: `feishu_crm.ipg_clients`
   - Search field: `client_name`
   - Display: Orange badge

3. **QD Enterprises** (268 records)
   - Database: `enterprise_QD.enterprise_QD`
   - Search field: `company_name`
   - Display: Blue badge

4. **Work Orders** (86 records)
   - Database: `Task_sync_new.task_service_records`
   - Search field: `customer_company`
   - Display: Red badge

## File Structure

### New Files Created

```
city_brain_frontend_v2/
├── src/
│   ├── types/
│   │   └── opportunities.ts                    # Type definitions
│   ├── services/
│   │   └── opportunitiesService.ts            # Opportunities API
│   ├── stores/
│   │   └── opportunitiesStore.ts              # Opportunities state
│   └── components/
│       └── data/
│           ├── OpportunityCard.vue            # Universal card component
│           └── StatisticsPanel.vue            # Statistics display
```

### Modified Files

```
city_brain_frontend_v2/
├── src/
│   ├── views/
│   │   ├── dashboard/DashboardView.vue        # Extended with opportunities
│   │   ├── insights/InsightsView.vue          # Completely refactored
│   │   └── operations/OperationsView.vue      # Completely refactored
│   ├── services/
│   │   ├── insightsService.ts                 # Removed time-series API
│   │   └── operationsService.ts               # Removed create ticket
│   ├── router/
│   │   └── index.ts                           # Commented Planning/Admin
│   └── components/
│       └── layout/
│           └── SidebarNav.vue                 # Updated menu items
```

### Preserved Files (For Future)

Planning and Admin views are preserved but not routed:
- `src/views/planning/PlanningView.vue` - For future spatial data integration
- `src/views/admin/AdminView.vue` - For future authentication system

## Testing Checklist

### Manual Testing Required

- [ ] **Dashboard View**
  - [ ] Company search works correctly
  - [ ] Opportunities auto-load after company query
  - [ ] AS/IPG/QD/WorkOrder sections display properly
  - [ ] OpportunityCard badges show correct colors
  - [ ] Empty states display when no data

- [ ] **Insights View**
  - [ ] Statistics panels load AS/IPG data
  - [ ] Status distribution displays correctly
  - [ ] System selector switches between AS/IPG
  - [ ] Search results display in table
  - [ ] Empty states for no results

- [ ] **Operations View**
  - [ ] Work order search by company name
  - [ ] Work order cards display all fields
  - [ ] Priority color coding (高=red, 中=orange, 低=green)
  - [ ] Statistics panel shows correct counts
  - [ ] Engineer info displays when available

- [ ] **Navigation**
  - [ ] Only 3 menu items visible (Dashboard, Insights, Operations)
  - [ ] Menu labels match page titles
  - [ ] Active state highlights current page
  - [ ] No broken links

- [ ] **API Integration**
  - [ ] All API calls use correct endpoints
  - [ ] Error handling displays user-friendly messages
  - [ ] Loading states show during API calls
  - [ ] Response data maps correctly to TypeScript types

### Integration Testing

```bash
# Start backend
cd city_brain_system_refactored
python3 main.py

# Start V2 frontend
cd city_brain_frontend_v2
npm run dev

# Test scenarios
1. Search "临工重机" in Dashboard → Verify opportunities load
2. Navigate to Insights → Verify statistics display
3. Search "临工" in Insights AS system → Verify results
4. Navigate to Operations → Search "临工" → Verify work orders
```

## Git Workflow

### Branch Strategy

1. ✅ Created feature branch: `feature/v2-frontend-refactor`
2. ✅ Pushed to remote: `origin/feature/v2-frontend-refactor`
3. ⏳ **Pending**: Manual testing
4. ⏳ **Pending**: Merge to `main` after approval

### Commits

```bash
# Initial refactoring commit
git commit -m "refactor(v2-frontend): align with backend data sources

Major changes:
- Create OpportunityCard/StatisticsPanel reusable components
- Refactor Dashboard to integrate opportunities/work orders
- Refactor Insights to use statistics API instead of time-series
- Refactor Operations to query-only (remove create form)
- Comment out Planning/Admin routes (no backend support)
- Update navigation menu to show only active modules
- Add TypeScript types matching Python backend models

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Next Steps

### Immediate (Before Merge)

1. **Manual Testing**: Complete testing checklist above
2. **Bug Fixes**: Address any issues found during testing
3. **Code Review**: Review changes with team
4. **Documentation**: Update user-facing docs if needed

### Future Enhancements (After Merge)

1. **Planning Module**: Implement when backend adds spatial data API
2. **Admin Module**: Implement when backend adds authentication system
3. **Real-time Updates**: Add WebSocket for live data updates
4. **Advanced Filters**: Add more search/filter options
5. **Data Export**: Add CSV/Excel export functionality
6. **Charts**: Add data visualization for statistics

## Lessons Learned

### What Worked Well

1. **Type-First Approach**: Creating TypeScript types matching backend models prevented runtime errors
2. **Component Reusability**: OpportunityCard works for all 4 data sources, reducing code duplication
3. **Progressive Enhancement**: Commenting out code instead of deleting preserves future work
4. **Separation of Concerns**: Clear service layer makes API changes easier to manage

### What to Improve

1. **Earlier API Verification**: Should verify backend APIs before frontend design
2. **Continuous Integration**: Need automated tests to catch type mismatches
3. **Documentation**: Should document API contracts in shared schema files
4. **Error Handling**: Could use more specific error types and better user feedback

## References

- **Backend Docs**: `docs/guides/DEVELOPMENT_GUIDE.md`
- **Architecture**: `docs/architecture/system-architecture.md`
- **API Docs**: http://localhost:9003/docs
- **CLAUDE.md**: Root-level guidance for AI assistants
