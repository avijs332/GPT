import { PropsWithChildren, useEffect } from 'react';
import { motion } from 'framer-motion';

import { useLayout } from '../layout';

const pageVariants = {
  initial: { opacity: 0, x: 40 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -40 },
};

interface WrapperProps {
  shouldSpread: boolean;
  shouldPad: boolean;
};

export const MotionWrapper = ({ shouldPad, shouldSpread, children }: PropsWithChildren<WrapperProps>) => {
  const { spread, unSpread, pad, unPad } = useLayout();

  useEffect(() => {
    if (shouldSpread) {
      spread();
    } else {
      unSpread();
    };

    if (shouldPad) {
      pad();
    } else {
      unPad();
    };
  }, []);

  return (
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
};