import { Route, Routes } from "react-router"

import BusRouteMap from "./map"
import { AppProviders } from "./providers"
import { PlanningPage } from "./planning"
import { PreparePage } from "./prepare_map"

const App = () => (
  <AppProviders>
    <Routes>
      <Route path="/" element={<PlanningPage />} />
      <Route path="/prepare" element={<PreparePage />} />
      <Route path="/map" element={<BusRouteMap />} />
    </Routes>
  </AppProviders>
)

export default App
