import { Route, Routes } from "react-router"

import BusRouteMap from "./predict"
import { AppProviders } from "./providers"
import { PlanningPage } from "./first-details"
import { PreparePage } from "./prepare-map"
import { Home } from "./home"
import { LayoutWrapper } from "./common/LayoutWrapper"

const App = () => (
  <AppProviders>
    <LayoutWrapper>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/plan" element={<PlanningPage />} />
        <Route path="/prepare" element={<PreparePage />} />
        <Route path="/map" element={<BusRouteMap />} />
      </Routes>
    </LayoutWrapper>
  </AppProviders>
)

export default App
