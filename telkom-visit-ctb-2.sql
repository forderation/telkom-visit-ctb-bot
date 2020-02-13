-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 13, 2020 at 07:59 AM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.4.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `telkom-visit-ctb-2`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `ID` int(11) NOT NULL,
  `PASSWORD` text NOT NULL,
  `LAST_LOGIN` datetime DEFAULT NULL,
  `USERNAME` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`ID`, `PASSWORD`, `LAST_LOGIN`, `USERNAME`) VALUES
(1, 'd3d9446802a44259755d38e6d163e820', '2020-02-13 13:50:35', 'muzaki_gh');

-- --------------------------------------------------------

--
-- Table structure for table `category_result`
--

CREATE TABLE `category_result` (
  `ID_CATEGORY` int(11) NOT NULL,
  `ID_STATE` int(11) DEFAULT NULL,
  `NAME_CATEGORY` text NOT NULL,
  `CODE_CATEGORY` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `category_result`
--

INSERT INTO `category_result` (`ID_CATEGORY`, `ID_STATE`, `NAME_CATEGORY`, `CODE_CATEGORY`) VALUES
(2, 2, 'customer', 'CS'),
(3, 2, 'product', 'PD'),
(4, 2, 'service', 'S'),
(5, 3, 'not found', 'NF');

-- --------------------------------------------------------

--
-- Table structure for table `photo_visit`
--

CREATE TABLE `photo_visit` (
  `ID_PHOTO` int(11) NOT NULL,
  `ID_VISITOR` bigint(20) DEFAULT NULL,
  `ID_HIST` int(11) DEFAULT NULL,
  `PHOTO_PATH` text NOT NULL,
  `PH_DATE_SUBMIT` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `photo_visit`
--

INSERT INTO `photo_visit` (`ID_PHOTO`, `ID_VISITOR`, `ID_HIST`, `PHOTO_PATH`, `PH_DATE_SUBMIT`) VALUES
(1, 507549293, 1, 'C:\\Users\\zaki\\telkom-chatbot-telegram/res/img/2020-02-13/507549293/AgACAgUAAxkBAAIORl5E7t1pR318ywgT2-gQXeNA7a39AAI-qTEbamUgVkBUHv4HLQsvYbolMwAEAQADAgADeAADwWIDAAEYBA.jpg', '2020-02-13 13:38:28'),
(2, 507549293, 2, 'C:\\Users\\zaki\\telkom-chatbot-telegram/res/img/2020-02-13/507549293/AgACAgUAAxkBAAIOS15E7wkSeAy2422jcK-ARuuw-5k7AAJAqTEbamUgVt_PrPE9T7cUvPJqanQAAwEAAwIAA3gAA1k9AAIYBA.jpg', '2020-02-13 13:39:10');

-- --------------------------------------------------------

--
-- Table structure for table `state_visit`
--

CREATE TABLE `state_visit` (
  `ID_STATE` int(11) NOT NULL,
  `NAME_STATE` text NOT NULL,
  `CODE_STATE` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `state_visit`
--

INSERT INTO `state_visit` (`ID_STATE`, `NAME_STATE`, `CODE_STATE`) VALUES
(2, 'contacted', 'A'),
(3, 'not contacted', 'B');

-- --------------------------------------------------------

--
-- Table structure for table `todo_list`
--

CREATE TABLE `todo_list` (
  `ID_TODO` int(11) NOT NULL,
  `ID_VISITOR` bigint(20) DEFAULT NULL,
  `NIP` bigint(20) DEFAULT NULL,
  `TD_DATE` date DEFAULT NULL,
  `IS_SUBMIT` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `todo_list`
--

INSERT INTO `todo_list` (`ID_TODO`, `ID_VISITOR`, `NIP`, `TD_DATE`, `IS_SUBMIT`) VALUES
(1, 507549293, 152504308719, '2020-02-13', 1),
(2, 507549293, 152504302224, '2020-02-13', 0),
(3, 507549293, 152504303748, '2020-02-13', 0),
(4, 507549293, 152504307600, '2020-02-13', 0),
(5, 507549293, 152504305667, '2020-02-13', 0),
(6, 507549293, 152504303067, '2020-02-13', 0);

-- --------------------------------------------------------

--
-- Table structure for table `visitor`
--

CREATE TABLE `visitor` (
  `ID_VISITOR` bigint(20) NOT NULL,
  `NAME_VISITOR` varchar(50) NOT NULL,
  `USERNAME` varchar(30) NOT NULL,
  `TOTAL_SUBMIT` int(11) DEFAULT NULL,
  `VS_LAST_SUBMIT` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `visitor`
--

INSERT INTO `visitor` (`ID_VISITOR`, `NAME_VISITOR`, `USERNAME`, `TOTAL_SUBMIT`, `VS_LAST_SUBMIT`) VALUES
(123569293, 'Harris Ishaq', 'harris', 7, '2020-02-04 00:00:00'),
(453435435, 'Madina Ali', 'ali', 5, '2020-02-03 00:00:00'),
(507549112, 'Ibrahim Mustofa', 'mustofa', 3, '2020-02-01 00:00:00'),
(507549293, 'Kharisma Muzaki', 'muzaki_gh', 5, '2020-02-13 13:39:10'),
(521335435, 'Wahyu Iskandar', 'wahyu', 6, '2020-02-10 00:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `visitor_todo`
--

CREATE TABLE `visitor_todo` (
  `ID_VISITOR_TODO` int(11) NOT NULL,
  `ID_VISITOR` bigint(20) DEFAULT NULL,
  `DATE` date DEFAULT NULL,
  `TODO_DONE` int(11) DEFAULT 0,
  `TODO_WAIT` int(11) DEFAULT 0,
  `OUTER_SUBMIT` int(11) DEFAULT 0,
  `VTD_LAST_SUBMIT` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `visitor_todo`
--

INSERT INTO `visitor_todo` (`ID_VISITOR_TODO`, `ID_VISITOR`, `DATE`, `TODO_DONE`, `TODO_WAIT`, `OUTER_SUBMIT`, `VTD_LAST_SUBMIT`) VALUES
(1, 507549293, '2020-02-13', 4, 5, 3, '13:39:10'),
(2, 123569293, '2020-02-13', 4, 2, 6, '13:39:10'),
(3, 507549112, '2020-02-13', 5, 6, 2, '13:39:10'),
(4, 453435435, '2020-02-13', 5, 2, 1, '13:39:10'),
(5, 521335435, '2020-02-13', 4, 7, 2, '13:39:10');

-- --------------------------------------------------------

--
-- Table structure for table `visit_hist`
--

CREATE TABLE `visit_hist` (
  `ID_HIST` int(11) NOT NULL,
  `ID_CATEGORY` int(11) DEFAULT NULL,
  `ID_STATE` int(11) DEFAULT NULL,
  `ID_RESULT` int(11) DEFAULT NULL,
  `ID_VISITOR` bigint(20) DEFAULT NULL,
  `HS_DATE_SUBMIT` datetime NOT NULL,
  `NIP` bigint(20) NOT NULL,
  `OTHER_DESC` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `visit_hist`
--

INSERT INTO `visit_hist` (`ID_HIST`, `ID_CATEGORY`, `ID_STATE`, `ID_RESULT`, `ID_VISITOR`, `HS_DATE_SUBMIT`, `NIP`, `OTHER_DESC`) VALUES
(1, 3, 2, 12, 507549293, '2020-02-13 13:38:28', 152504308719, 'rumah tutup yns kerja semua cp08191341232'),
(2, 3, 2, 10, 507549293, '2020-02-13 13:39:10', 152504308333, 'rumah tutup yns kerja semua cp08191341232');

-- --------------------------------------------------------

--
-- Table structure for table `visit_result`
--

CREATE TABLE `visit_result` (
  `ID_RESULT` int(11) NOT NULL,
  `ID_CATEGORY` int(11) DEFAULT NULL,
  `ID_STATE` int(11) DEFAULT NULL,
  `NAME_RESULT` text NOT NULL,
  `CODE_RESULT` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `visit_result`
--

INSERT INTO `visit_result` (`ID_RESULT`, `ID_CATEGORY`, `ID_STATE`, `NAME_RESULT`, `CODE_RESULT`) VALUES
(2, 2, 2, 'jarang digunakan', '1'),
(3, 2, 2, 'kendala keuangan', '2'),
(4, 2, 2, 'lupa bayar', '3'),
(5, 2, 2, 'pindah ke kompetitor', '4'),
(6, 2, 2, 'sudah ada internet lain', '5'),
(7, 2, 2, 'sudah bayar', '6'),
(8, 2, 2, 'tidak sempat bayar sibuk', '7'),
(9, 2, 2, 'tidak tahu tagihan', '8'),
(10, 3, 2, 'koneksi lambat', '1'),
(11, 3, 2, 'putus', '2'),
(12, 3, 2, 'tidak bisa browsing / GGN', '3'),
(13, 4, 2, 'gangguan belum diselesaikan', '1'),
(14, 4, 2, 'internet belum aktif', '2'),
(15, 4, 2, 'tidak merasa pasang', '3'),
(16, 5, 3, 'alamat tidak ada', '1'),
(17, 5, 3, 'bukan pelanggan yang bersangkutan', '2'),
(18, 5, 3, 'tidak bertemu penghuni', '3'),
(19, 5, 3, 'rumah tidak berpenghuni', '4');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `category_result`
--
ALTER TABLE `category_result`
  ADD PRIMARY KEY (`ID_CATEGORY`),
  ADD KEY `FK_CATEGORY_RELATIONS_STATE_VI` (`ID_STATE`);

--
-- Indexes for table `photo_visit`
--
ALTER TABLE `photo_visit`
  ADD PRIMARY KEY (`ID_PHOTO`),
  ADD KEY `FK_PHOTO_VI_RELATIONS_VISIT_HI` (`ID_HIST`),
  ADD KEY `FK_PHOTO_VI_RELATIONS_VISITOR` (`ID_VISITOR`);

--
-- Indexes for table `state_visit`
--
ALTER TABLE `state_visit`
  ADD PRIMARY KEY (`ID_STATE`);

--
-- Indexes for table `todo_list`
--
ALTER TABLE `todo_list`
  ADD PRIMARY KEY (`ID_TODO`),
  ADD KEY `FK_TODO_LIS_RELATIONS_VISITOR` (`ID_VISITOR`);

--
-- Indexes for table `visitor`
--
ALTER TABLE `visitor`
  ADD PRIMARY KEY (`ID_VISITOR`);

--
-- Indexes for table `visitor_todo`
--
ALTER TABLE `visitor_todo`
  ADD PRIMARY KEY (`ID_VISITOR_TODO`),
  ADD KEY `FK_VISITOR__RELATIONS_VISITOR` (`ID_VISITOR`);

--
-- Indexes for table `visit_hist`
--
ALTER TABLE `visit_hist`
  ADD PRIMARY KEY (`ID_HIST`),
  ADD KEY `FK_VISIT_HI_RELATIONS_VISITOR` (`ID_VISITOR`),
  ADD KEY `FK_VISIT_HI_RELATIONS_STATE_VI` (`ID_STATE`),
  ADD KEY `FK_VISIT_HI_RELATIONS_VISIT_RE` (`ID_RESULT`),
  ADD KEY `FK_VISIT_HI_RELATIONS_CATEGORY` (`ID_CATEGORY`);

--
-- Indexes for table `visit_result`
--
ALTER TABLE `visit_result`
  ADD PRIMARY KEY (`ID_RESULT`),
  ADD KEY `FK_VISIT_RE_RELATIONS_CATEGORY` (`ID_CATEGORY`),
  ADD KEY `FK_VISIT_RE_RELATIONS_STATE_VI` (`ID_STATE`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `category_result`
--
ALTER TABLE `category_result`
  MODIFY `ID_CATEGORY` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `photo_visit`
--
ALTER TABLE `photo_visit`
  MODIFY `ID_PHOTO` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `state_visit`
--
ALTER TABLE `state_visit`
  MODIFY `ID_STATE` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `todo_list`
--
ALTER TABLE `todo_list`
  MODIFY `ID_TODO` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `visitor`
--
ALTER TABLE `visitor`
  MODIFY `ID_VISITOR` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=521335436;

--
-- AUTO_INCREMENT for table `visitor_todo`
--
ALTER TABLE `visitor_todo`
  MODIFY `ID_VISITOR_TODO` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `visit_hist`
--
ALTER TABLE `visit_hist`
  MODIFY `ID_HIST` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `visit_result`
--
ALTER TABLE `visit_result`
  MODIFY `ID_RESULT` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `category_result`
--
ALTER TABLE `category_result`
  ADD CONSTRAINT `FK_CATEGORY_RELATIONS_STATE_VI` FOREIGN KEY (`ID_STATE`) REFERENCES `state_visit` (`ID_STATE`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `photo_visit`
--
ALTER TABLE `photo_visit`
  ADD CONSTRAINT `FK_PHOTO_VI_RELATIONS_VISITOR` FOREIGN KEY (`ID_VISITOR`) REFERENCES `visitor` (`ID_VISITOR`) ON UPDATE CASCADE,
  ADD CONSTRAINT `FK_PHOTO_VI_RELATIONS_VISIT_HI` FOREIGN KEY (`ID_HIST`) REFERENCES `visit_hist` (`ID_HIST`);

--
-- Constraints for table `todo_list`
--
ALTER TABLE `todo_list`
  ADD CONSTRAINT `FK_TODO_LIS_RELATIONS_VISITOR` FOREIGN KEY (`ID_VISITOR`) REFERENCES `visitor` (`ID_VISITOR`) ON UPDATE CASCADE;

--
-- Constraints for table `visitor_todo`
--
ALTER TABLE `visitor_todo`
  ADD CONSTRAINT `FK_VISITOR__RELATIONS_VISITOR` FOREIGN KEY (`ID_VISITOR`) REFERENCES `visitor` (`ID_VISITOR`) ON UPDATE CASCADE;

--
-- Constraints for table `visit_hist`
--
ALTER TABLE `visit_hist`
  ADD CONSTRAINT `FK_VISIT_HI_RELATIONS_CATEGORY` FOREIGN KEY (`ID_CATEGORY`) REFERENCES `category_result` (`ID_CATEGORY`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `FK_VISIT_HI_RELATIONS_STATE_VI` FOREIGN KEY (`ID_STATE`) REFERENCES `state_visit` (`ID_STATE`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `FK_VISIT_HI_RELATIONS_VISITOR` FOREIGN KEY (`ID_VISITOR`) REFERENCES `visitor` (`ID_VISITOR`) ON UPDATE CASCADE,
  ADD CONSTRAINT `FK_VISIT_HI_RELATIONS_VISIT_RE` FOREIGN KEY (`ID_RESULT`) REFERENCES `visit_result` (`ID_RESULT`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `visit_result`
--
ALTER TABLE `visit_result`
  ADD CONSTRAINT `FK_VISIT_RE_RELATIONS_CATEGORY` FOREIGN KEY (`ID_CATEGORY`) REFERENCES `category_result` (`ID_CATEGORY`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `FK_VISIT_RE_RELATIONS_STATE_VI` FOREIGN KEY (`ID_STATE`) REFERENCES `state_visit` (`ID_STATE`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
