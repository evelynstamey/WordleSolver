CREATE DATABASE IF NOT EXISTS WordleSolver;
USE WordleSolver;

DROP TABLE IF EXISTS `WordleSolver`.`clues`;
CREATE TABLE IF NOT EXISTS `WordleSolver`.`clues` (
  `row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `game_id` VARCHAR(40) NULL,
  `round_id` BIGINT NULL,
  `guess` CHAR(5) NULL,
  `_not_in_word` JSON NULL,
  `_at_not_index` JSON NULL,
  `_at_index` JSON NULL,
  `not_in_word` JSON NULL,
  `at_not_index` JSON NULL,
  `at_index` JSON NULL
);

DROP PROCEDURE IF EXISTS `sp_WriteClues`;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_WriteClues`(
  IN i_user_id VARCHAR(40),
  IN i_round_id BIGINT,
  IN i_guess CHAR(5),
  IN i__not_in_word JSON,
  IN i__at_not_index JSON,
  IN i__at_index JSON,
  IN i_not_in_word JSON,
  IN i_at_not_index JSON,
  IN i_at_index JSON
)
BEGIN
	INSERT INTO `WordleSolver`.`clues`
	(
    game_id,
    round_id,
    guess,
    _not_in_word,
    _at_not_index,
    _at_index,
    not_in_word,
    at_not_index,
    at_index
	)
	VALUES
	(
    i_user_id,
    i_round_id,
    i_guess,
    i__not_in_word,
    i__at_not_index,
    i__at_index,
    i_not_in_word,
    i_at_not_index,
    i_at_index
	);
END $$
DELIMITER ;

DROP TABLE IF EXISTS `WordleSolver`.`corpus`;
CREATE TABLE IF NOT EXISTS `WordleSolver`.`corpus` (
  `row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `game_id` VARCHAR(40) NULL,
  `round_id` BIGINT NULL,
  `corpus` JSON NULL
);

DROP PROCEDURE IF EXISTS `sp_WriteCorpus`;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_WriteCorpus`(
  IN i_user_id VARCHAR(40),
  IN i_round_id BIGINT,
  IN i_corpus JSON
)
BEGIN
	INSERT INTO `WordleSolver`.`corpus`
	(
    game_id,
    round_id,
    corpus
	)
	VALUES
	(
    i_user_id,
    i_round_id,
    i_corpus
	);
END $$
DELIMITER ;
