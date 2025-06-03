import { PropsWithChildren } from 'react';
import { motion } from 'framer-motion';

const pageVariants = {
  initial: { opacity: 0, x: 40 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -40 },
};

export const MotionWrapper = ({ children }: PropsWithChildren) => (
  <motion.div
    variants={pageVariants}
    initial="initial"
    animate="animate"
    exit="exit"
    transition={{ duration: 0.4, ease: 'easeInOut' }}
    style={{ width: '100%' }}
  >
    {children}
  </motion.div>
);