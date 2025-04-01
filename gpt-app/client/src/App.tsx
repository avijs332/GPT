import { Route, Routes } from "react-router"

import BusRouteMap from "./map"
import { AppProviders } from "./providers"
import { PlanningPage } from "./planning"

const App = () => (
  <AppProviders>
    <Routes>
      <Route path="/" element={<PlanningPage />} />
      <Route path="/map" element={<BusRouteMap />} />
    </Routes>
  </AppProviders>
)

export default App
